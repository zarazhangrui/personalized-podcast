"""
Stage 4: Publish — Push the podcast episode to GitHub Pages.

This is the delivery mechanism. It takes your freshly generated MP3 file,
uploads it to a GitHub Pages repository, and updates the RSS feed XML
so podcast players automatically pick up the new episode.

Think of it like a radio station: the MP3 is the recording, and the RSS
feed is the broadcast signal. Podcast players tune into your feed URL
and automatically download new episodes when they appear.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import formatdate
from pathlib import Path
from time import mktime

from jinja2 import Template

# Allow importing utils from the same directory
sys.path.insert(0, str(Path(__file__).parent))
from utils import get_data_dir, get_skill_dir, load_config, load_env, setup_logging


def get_audio_duration(mp3_path):
    """
    Returns the duration of an MP3 file in HH:MM:SS format.
    Uses pydub to read the audio file's metadata.
    """
    from pydub import AudioSegment
    audio = AudioSegment.from_mp3(str(mp3_path))
    total_seconds = len(audio) / 1000
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def check_gh_auth(logger):
    """
    Verifies the GitHub CLI is installed and authenticated.
    Raises a helpful error if not.
    """
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "GitHub CLI is not authenticated.\n\n"
                "Run this command to log in:\n"
                "  gh auth login\n\n"
                "Follow the prompts to authenticate with your GitHub account."
            )
        logger.info("GitHub CLI authenticated")
    except FileNotFoundError:
        raise RuntimeError(
            "GitHub CLI (gh) is not installed.\n\n"
            "To install it:\n"
            "  macOS:   brew install gh\n"
            "  Ubuntu:  sudo apt install gh\n\n"
            "Then run: gh auth login"
        )


def publish_episode(mp3_path, config, logger=None, episode_title=None, episode_description=None):
    """
    Publishes a podcast episode to GitHub Pages.

    How it works:
    1. Clones your podcast GitHub repo (quick shallow clone)
    2. Copies the new MP3 file into the repo's episodes/ folder
    3. Updates the RSS feed XML with the new episode's info
    4. Pushes everything back to GitHub
    5. GitHub Pages automatically serves the updated files

    The RSS feed URL never changes, so podcast players that subscribed
    to it will pick up the new episode within minutes.

    Args:
        mp3_path: Path to the MP3 file to publish
        config: Your parsed config.yaml
        logger: Logger instance

    Returns:
        The feed URL (for logging/confirmation)
    """
    if logger is None:
        logger = setup_logging()

    mp3_path = Path(mp3_path)
    if not mp3_path.exists():
        raise FileNotFoundError(f"MP3 file not found: {mp3_path}")

    publish_config = config.get("publish", {})
    github_repo = publish_config.get("github_repo")
    # Support both old (base_url) and new (base_url) config keys
    base_url = publish_config.get("base_url") or publish_config.get("base_url")

    if not github_repo:
        raise RuntimeError("publish.github_repo is not set in config.yaml")
    if not base_url:
        raise RuntimeError("publish.base_url is not set in config.yaml")

    # Verify GitHub CLI is authenticated
    check_gh_auth(logger)

    # Build episode metadata
    filename = mp3_path.name
    file_size = mp3_path.stat().st_size
    duration = get_audio_duration(mp3_path)
    now = datetime.now(timezone.utc)
    # RFC 2822 date format (required by RSS spec)
    pub_date = formatdate(timeval=now.timestamp(), localtime=False, usegmt=True)

    episode = {
        "title": episode_title or f"{config.get('show_name', 'Daily Digest')} — {now.strftime('%B %d, %Y')}",
        "description": episode_description or f"Your personalized podcast for {now.strftime('%B %d, %Y')}",
        "pub_date": pub_date,
        "filename": filename,
        "file_size": str(file_size),
        "duration": duration,
        "guid": f"{base_url}/episodes/{filename}",
    }

    # Work in a temp directory for git operations
    with tempfile.TemporaryDirectory() as tmp_dir:
        repo_dir = Path(tmp_dir) / "repo"

        # Clone the repo (shallow for speed)
        logger.info(f"Cloning {github_repo}...")
        result = subprocess.run(
            ["gh", "repo", "clone", github_repo, str(repo_dir), "--", "--depth", "1"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to clone repo: {result.stderr}")

        # Create episodes directory if it doesn't exist
        episodes_dir = repo_dir / "episodes"
        episodes_dir.mkdir(exist_ok=True)

        # Copy the MP3 file
        dest_mp3 = episodes_dir / filename
        shutil.copy2(str(mp3_path), str(dest_mp3))
        logger.info(f"Copied {filename} to repo ({file_size / (1024*1024):.1f}MB)")

        # Build the full episode list by scanning existing episodes + new one
        episodes = _scan_existing_episodes(repo_dir, config, logger)
        episodes.append(episode)

        # Sort by date (newest first for the RSS feed)
        # Parse RFC 2822 dates properly for sorting (string sort doesn't work)
        from email.utils import parsedate_to_datetime
        episodes.sort(key=lambda e: parsedate_to_datetime(e["pub_date"]), reverse=True)

        # Enforce retention limit — delete oldest episodes if we're over the limit
        max_episodes = config.get("retention", {}).get("max_episodes", 30)
        deleted_any = False
        if len(episodes) > max_episodes:
            old_episodes = episodes[max_episodes:]
            episodes = episodes[:max_episodes]
            for old in old_episodes:
                old_file = episodes_dir / old["filename"]
                if old_file.exists():
                    old_file.unlink()
                    logger.info(f"Deleted old episode: {old['filename']}")
                    deleted_any = True

        # Render the RSS feed XML
        skill_dir = get_skill_dir()
        template_path = skill_dir / "templates" / "feed_template.xml"
        with open(template_path, "r") as f:
            template = Template(f.read())

        feed_xml = template.render(
            show_name=config.get("show_name", "My Podcast"),
            description=config.get("description", "A personalized AI-generated podcast."),
            owner_email=config.get("owner_email", ""),
            base_url=base_url,
            language=config.get("language", "en"),
            episodes=episodes,
        )

        # Validate the XML is well-formed before writing
        try:
            ET.fromstring(feed_xml)
        except ET.ParseError as e:
            raise RuntimeError(f"Generated feed XML is malformed: {e}")

        # Write the feed
        feed_path = repo_dir / "feed.xml"
        with open(feed_path, "w") as f:
            f.write(feed_xml)
        logger.info("Updated feed.xml")

        # Save episode list for future reference
        episodes_json_path = repo_dir / "episodes.json"
        with open(episodes_json_path, "w") as f:
            json.dump(episodes, f, indent=2)

        # Git add, commit, push
        logger.info("Pushing to GitHub...")
        _git_run(repo_dir, ["add", "."])
        _git_run(repo_dir, ["commit", "-m", f"Add episode: {now.strftime('%Y-%m-%d')}"])

        push_result = subprocess.run(
            ["git", "push"],
            cwd=str(repo_dir),
            capture_output=True,
            text=True,
        )
        if push_result.returncode != 0:
            raise RuntimeError(f"Git push failed: {push_result.stderr}")

        # Clean up git history if we deleted old episodes
        if deleted_any:
            logger.info("Running git gc to clean up deleted episode history...")
            subprocess.run(["git", "gc", "--aggressive", "--prune=now"], cwd=str(repo_dir), capture_output=True)

        feed_url = f"{base_url}/feed.xml"
        logger.info(f"Published! Feed URL: {feed_url}")
        return feed_url


def _scan_existing_episodes(repo_dir, config, logger):
    """
    Scans the repo for existing episode metadata.
    Reads from episodes.json if it exists, otherwise returns empty list.
    """
    episodes_json = repo_dir / "episodes.json"
    if episodes_json.exists():
        with open(episodes_json, "r") as f:
            return json.load(f)
    return []


def _git_run(repo_dir, args):
    """Helper to run git commands in the repo directory."""
    result = subprocess.run(
        ["git"] + args,
        cwd=str(repo_dir),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr}")
    return result


if __name__ == "__main__":
    """
    Run this directly to publish an episode:
      python publish.py --mp3 path/to/episode.mp3
      python publish.py  # Auto-finds latest MP3
    """
    import argparse

    parser = argparse.ArgumentParser(description="Publish a podcast episode to GitHub Pages")
    parser.add_argument("--mp3", help="Path to the MP3 file to publish (default: latest in episodes dir)")
    parser.add_argument("--title", help="Episode title (default: show name + date)")
    parser.add_argument("--description", help="Episode description")
    args = parser.parse_args()

    logger = setup_logging()
    load_env()
    config = load_config()

    if args.mp3:
        mp3_path = Path(args.mp3)
    else:
        # Find the latest MP3 in the episodes directory
        data_dir = get_data_dir()
        episodes_dir = data_dir / "episodes"
        mp3_files = sorted(episodes_dir.glob("*.mp3"))
        if not mp3_files:
            logger.error("No MP3 files found in episodes directory. Run speak.py first.")
            sys.exit(1)
        mp3_path = mp3_files[-1]

    logger.info(f"Publishing episode: {mp3_path.name}")
    feed_url = publish_episode(mp3_path, config, logger, episode_title=args.title, episode_description=args.description)
    print(f"\nPublished! Feed URL: {feed_url}")
