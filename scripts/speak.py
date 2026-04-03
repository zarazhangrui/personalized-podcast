"""
Stage: Speak — Convert the podcast script into audio using Fish Audio TTS.

Takes the conversation script (a list of speaker segments) and turns each
line into speech using Fish Audio's text-to-speech API. Each host gets
their own voice, and all the audio chunks get stitched together into
a single MP3 file.

Think of it like a recording studio session: each host reads their lines,
and the sound engineer edits them together into one smooth episode.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Allow importing utils from the same directory
sys.path.insert(0, str(Path(__file__).parent))
from utils import get_data_dir, load_config, load_env, setup_logging


def check_ffmpeg():
    """
    Checks that ffmpeg is installed (required by pydub for audio processing).
    Raises a helpful error if it's missing, with install instructions.
    """
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise FileNotFoundError()
    except FileNotFoundError:
        raise RuntimeError(
            "ffmpeg is not installed but is required for audio processing.\n\n"
            "To install it:\n"
            "  macOS:   brew install ffmpeg\n"
            "  Ubuntu:  sudo apt install ffmpeg\n"
            "  Windows: Download from https://ffmpeg.org/download.html\n\n"
            "After installing, run the pipeline again."
        )


def generate_audio(script_segments, config, logger=None):
    """
    Converts script segments into a single MP3 file.

    How it works:
    1. Checks ffmpeg is installed (needed for audio processing)
    2. For each line in the script, calls Fish Audio with the right voice
    3. Collects all the audio chunks
    4. Stitches them together with brief pauses between speakers
    5. Adds a gentle fade-in at the start and fade-out at the end
    6. Saves the final MP3 file

    Args:
        script_segments: List of {"speaker": "A"|"B", "text": "..."} dicts
        config: Your parsed config.yaml
        logger: Logger instance

    Returns:
        Path to the generated MP3 file
    """
    if logger is None:
        logger = setup_logging()

    # Step 1: Make sure ffmpeg is available
    check_ffmpeg()

    # Import audio libraries (pydub needs ffmpeg to work)
    from pydub import AudioSegment

    data_dir = get_data_dir()
    tts_config = config.get("tts", {})

    # Get Fish Audio API key
    api_key_env = tts_config.get("api_key_env", "FISH_API_KEY")
    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise RuntimeError(
            f"Fish Audio API key not found in environment variable '{api_key_env}'.\n"
            f"Make sure it's set in your .env file at ~/.claude/personalized-podcast/.env"
        )

    # Map speakers to Fish Audio voice reference IDs
    voice_map = {
        "A": tts_config.get("host_a_voice_id", ""),
        "B": tts_config.get("host_b_voice_id", ""),
    }

    # Validate voice IDs are set
    for speaker, voice_id in voice_map.items():
        if not voice_id:
            host_name = "Host A (Alex)" if speaker == "A" else "Host B (Sam)"
            raise RuntimeError(
                f"No voice ID set for {host_name}.\n"
                f"Browse voices at fish.audio/discovery, pick one, and add its "
                f"reference ID to config.yaml under tts.host_{speaker.lower()}_voice_id"
            )

    # Initialize Fish Audio client
    from fishaudio import FishAudio
    from fishaudio.utils import save as fish_save
    client = FishAudio(api_key=api_key)

    # Step 2: Generate audio for each segment
    logger.info(f"Generating TTS for {len(script_segments)} segments...")
    audio_chunks = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        for i, segment in enumerate(script_segments):
            speaker = segment["speaker"]
            text = segment["text"]
            voice_id = voice_map.get(speaker, voice_map["A"])

            speaker_name = "Alex" if speaker == "A" else "Sam"
            preview = text[:60] + "..." if len(text) > 60 else text
            logger.info(f"  Segment {i+1}/{len(script_segments)} ({speaker_name}): {preview}")

            try:
                # Call Fish Audio API — returns audio data
                audio = client.tts.convert(
                    text=text,
                    reference_id=voice_id,
                )

                # Save the audio chunk to a temp file
                chunk_path = Path(tmp_dir) / f"chunk_{i:04d}.mp3"
                fish_save(audio, str(chunk_path))
                audio_chunks.append(chunk_path)

            except Exception as e:
                logger.error(f"  TTS failed for segment {i+1}: {e}")
                if "quota" in str(e).lower() or "limit" in str(e).lower():
                    logger.warning(
                        f"  Quota/limit issue — stitching {len(audio_chunks)} "
                        f"of {len(script_segments)} segments into a partial episode."
                    )
                    break  # Stitch what we have instead of crashing
                raise

        if not audio_chunks:
            raise RuntimeError("No audio segments were generated. Check your Fish Audio API key and quota.")

        # Step 3: Stitch all chunks together
        logger.info("Stitching audio segments together...")

        # Create silence gap between speakers (300ms of quiet)
        silence = AudioSegment.silent(duration=300)

        # Load and combine all chunks
        combined = AudioSegment.empty()
        for i, chunk_path in enumerate(audio_chunks):
            chunk_audio = AudioSegment.from_mp3(str(chunk_path))
            if i > 0:
                # Add a brief silence between segments for natural pacing
                combined += silence
            combined += chunk_audio

        # Step 4: Add fade effects for a polished feel
        # Gentle fade-in at the start (500ms)
        combined = combined.fade_in(500)
        # Longer fade-out at the end (1000ms) for a smooth finish
        combined = combined.fade_out(1000)

        # Step 5: Export the final MP3
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        episodes_dir = data_dir / "episodes"
        episodes_dir.mkdir(parents=True, exist_ok=True)
        output_path = episodes_dir / f"{timestamp}.mp3"

        combined.export(str(output_path), format="mp3", bitrate="128k")

        # Log the results
        duration_seconds = len(combined) / 1000
        duration_min = int(duration_seconds // 60)
        duration_sec = int(duration_seconds % 60)
        file_size_mb = output_path.stat().st_size / (1024 * 1024)

        logger.info(f"Audio saved: {output_path}")
        logger.info(f"Duration: {duration_min}m {duration_sec}s | Size: {file_size_mb:.1f}MB")

        return output_path


if __name__ == "__main__":
    """
    Run this directly to generate audio from a saved script:
      python speak.py --script path/to/script.json
    """
    parser = argparse.ArgumentParser(description="Generate podcast audio from a script JSON file")
    parser.add_argument("--script", required=True, help="Path to the script JSON file")
    args = parser.parse_args()

    logger = setup_logging()
    load_env()
    config = load_config()

    with open(args.script, "r") as f:
        script = json.load(f)

    logger.info(f"Loaded script with {len(script)} segments")
    output_path = generate_audio(script, config, logger)
    print(f"\nAudio file created: {output_path}")
