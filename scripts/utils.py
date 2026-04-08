"""
Shared utilities for the Personalized Podcast pipeline.

This module is the "toolbox" that all other scripts reach into. It handles:
- Loading your config file (config.yaml)
- Loading your secret API keys (.env file)
- Setting up logging so you can see what's happening
- Reading/writing pipeline state (what was last processed)
- Finding the right directories for everything
"""

import json
import logging
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml
from dotenv import load_dotenv


def get_data_dir():
    """
    Returns the path to ~/.personalized-podcast/ and creates it
    (plus subdirectories) if it doesn't exist yet.

    Think of this as the "home base" for all your podcast data —
    config, logs, generated scripts, everything lives here.

    Backwards compatibility: if the old ~/.claude/personalized-podcast path
    exists and the new ~/.personalized-podcast path does not, the old path
    is used automatically so existing setups keep working without any migration.
    """
    data_dir = Path.home() / ".personalized-podcast"
    legacy_dir = Path.home() / ".claude" / "personalized-podcast"
    if legacy_dir.exists() and not data_dir.exists():
        data_dir = legacy_dir
    # Create all the subdirectories we need
    for subdir in ["logs", "scripts_output", "episodes"]:
        (data_dir / subdir).mkdir(parents=True, exist_ok=True)
    return data_dir


def get_skill_dir():
    """
    Returns the path to the skill's own directory (where SKILL.md lives).
    This is where templates and scripts are stored.
    """
    # This file lives in skills/personalized-podcast/scripts/utils.py
    # So the skill dir is two levels up
    return Path(__file__).parent.parent


def load_config(config_path=None):
    """
    Reads your config.yaml file and returns it as a Python dictionary.

    If no path is given, looks in the default location:
    ~/.personalized-podcast/config.yaml

    Raises a helpful error if the file is missing, so you know
    exactly what to do to fix it.
    """
    if config_path is None:
        config_path = get_data_dir() / "config.yaml"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found at {config_path}\n"
            f"Run the setup first: /personalized-podcast\n"
            f"Or copy the example: cp SKILL_DIR/config/config.example.yaml {config_path}"
        )

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config


def load_env(env_path=None):
    """
    Loads your .env file (which contains API keys) into the environment.

    The .env file keeps your secrets separate from the config file,
    so you never accidentally share them. It loads them as environment
    variables that the API libraries can find automatically.
    """
    if env_path is None:
        env_path = get_data_dir() / ".env"
    else:
        env_path = Path(env_path)

    if not env_path.exists():
        raise FileNotFoundError(
            f"Environment file not found at {env_path}\n"
            f"Create it with your API key:\n"
            f"  FISH_API_KEY=your_fish_audio_api_key_here"
        )

    load_dotenv(env_path)


def setup_logging(log_dir=None):
    """
    Sets up logging so every pipeline run creates a log file.

    Logs go to two places:
    1. A file: ~/.personalized-podcast/logs/YYYY-MM-DD.log
    2. The terminal (stdout) so you can watch in real time

    Returns a logger object that all scripts use to record what they're doing.
    """
    if log_dir is None:
        log_dir = get_data_dir() / "logs"

    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # One log file per day
    log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

    # Create a logger with a descriptive name
    logger = logging.getLogger("personalized-podcast")
    logger.setLevel(logging.DEBUG)

    # Don't add duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    # File handler — captures everything for debugging later
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )

    # Console handler — shows progress in real time
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def read_state(state_path=None):
    """
    Reads the pipeline's state file to know what was last processed.

    The state tracks:
    - last_run: when the pipeline last ran (ISO timestamp)
    - processed_ids: IDs of articles already turned into episodes

    If the state file doesn't exist yet (first run), returns empty defaults.
    """
    if state_path is None:
        state_path = get_data_dir() / "state.json"
    else:
        state_path = Path(state_path)

    if not state_path.exists():
        return {"last_run": None, "processed_ids": []}

    with open(state_path, "r") as f:
        return json.load(f)


def write_state(state, state_path=None):
    """
    Saves the pipeline's state to disk.

    Uses an "atomic write" pattern: writes to a temporary file first,
    then renames it. This prevents corruption if the process crashes
    mid-write — you either get the old state or the new state, never
    a half-written mess.
    """
    if state_path is None:
        state_path = get_data_dir() / "state.json"
    else:
        state_path = Path(state_path)

    # Write to a temp file in the same directory, then rename
    # (rename is atomic on the same filesystem)
    tmp_path = state_path.with_suffix(".json.tmp")
    with open(tmp_path, "w") as f:
        json.dump(state, f, indent=2)
    tmp_path.rename(state_path)
