#!/usr/bin/env python3
"""
Bootstrap — First-run setup for the Personalized Podcast skill.

This script handles all the one-time setup:
1. Creates the data directory and Python virtual environment
2. Installs all Python dependencies
3. Checks that system tools (ffmpeg, gh) are available
4. Creates the .env file for API keys
5. Creates config.yaml from provided settings
6. Sets up a GitHub Pages repo for hosting the podcast feed
7. Pushes an initial commit so GitHub Pages has something to serve

You normally don't run this directly — the SKILL.md onboarding flow
calls it for you. But you can run it manually if needed.

Usage:
  python bootstrap.py --config-json '{"show_name": "My Show", ...}'
  python bootstrap.py  # Interactive mode (prompts for each setting)
"""

import argparse
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Set up Personalized Podcast")
    parser.add_argument(
        "--config-json",
        help="JSON string with config values (non-interactive mode)",
    )
    parser.add_argument(
        "--skip-repo",
        action="store_true",
        help="Skip GitHub repo creation (if you already have one)",
    )
    args = parser.parse_args()

    skill_dir = Path(__file__).parent.parent
    data_dir = Path.home() / ".personalized-podcast"

    print("=" * 60)
    print("Personalized Podcast — Setup")
    print("=" * 60)

    # =========================================================
    # Step 1: Create data directory structure
    # =========================================================
    print("\n[1/7] Creating data directories...")
    for subdir in ["logs", "scripts_output", "episodes"]:
        (data_dir / subdir).mkdir(parents=True, exist_ok=True)
    print(f"  Created: {data_dir}")

    # =========================================================
    # Step 2: Create Python virtual environment
    # =========================================================
    print("\n[2/7] Setting up Python virtual environment...")
    venv_dir = data_dir / "venv"

    if not venv_dir.exists():
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"  Error creating venv: {result.stderr}")
            sys.exit(1)
        print(f"  Created venv at: {venv_dir}")
    else:
        print(f"  Venv already exists at: {venv_dir}")

    # =========================================================
    # Step 3: Install Python dependencies
    # =========================================================
    print("\n[3/7] Installing Python dependencies...")
    pip_path = venv_dir / "bin" / "pip"
    requirements_path = skill_dir / "scripts" / "requirements.txt"

    result = subprocess.run(
        [str(pip_path), "install", "-r", str(requirements_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  Error installing dependencies: {result.stderr}")
        sys.exit(1)
    print("  All dependencies installed!")

    # =========================================================
    # Step 4: Check system dependencies
    # =========================================================
    print("\n[4/7] Checking system dependencies...")

    # Check ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("  ffmpeg: installed")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("  ffmpeg: NOT FOUND")
        print("  Install with: brew install ffmpeg")
        print("  Then run this setup again.")
        sys.exit(1)

    # Check gh CLI (optional — only needed for RSS feed publishing)
    gh_available = False
    try:
        result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
        if result.returncode == 0:
            print("  GitHub CLI: installed and authenticated")
            gh_available = True
        else:
            print("  GitHub CLI: installed but NOT authenticated (RSS publishing disabled)")
            print("  Run 'gh auth login' later to enable RSS feed publishing.")
    except FileNotFoundError:
        print("  GitHub CLI: not installed (RSS publishing disabled)")
        print("  Install with: brew install gh  (only needed for RSS feed publishing)")

    # =========================================================
    # Step 5: Create .env file (for API keys)
    # =========================================================
    print("\n[5/7] Setting up API key file...")
    env_path = data_dir / ".env"

    if not env_path.exists():
        env_content = textwrap.dedent("""\
            # Personalized Podcast API Keys
            # Paste your API key below (replace the placeholder text)

            # Get your Fish Audio API key from: https://fish.audio (profile/settings)
            FISH_API_KEY=paste-your-fish-audio-key-here
        """)
        with open(env_path, "w") as f:
            f.write(env_content)
        print(f"  Created: {env_path}")
        print("  IMPORTANT: You need to paste your API keys into this file!")
    else:
        print(f"  .env already exists at: {env_path}")

    # =========================================================
    # Step 6: Create config.yaml
    # =========================================================
    print("\n[6/7] Creating configuration...")
    config_path = data_dir / "config.yaml"

    if args.config_json:
        config_values = json.loads(args.config_json)
    else:
        # Use defaults — the SKILL.md onboarding will customize later
        config_values = {}

    if not config_path.exists() or args.config_json:
        # Start from the example config
        example_config = skill_dir / "config" / "config.example.yaml"
        with open(example_config, "r") as f:
            config_content = f.read()

        # Apply any provided values using string replacement on the YAML
        # (avoids needing PyYAML in system Python — it's in the venv only)
        if config_values:
            if "show_name" in config_values:
                config_content = config_content.replace(
                    'show_name: "My Daily Digest"',
                    f'show_name: "{config_values["show_name"]}"'
                )
            if "hosts" in config_values:
                config_content = config_content.replace(
                    "hosts: 2", f"hosts: {config_values['hosts']}"
                )
            if "length_minutes" in config_values:
                config_content = config_content.replace(
                    "length_minutes: 10", f"length_minutes: {config_values['length_minutes']}"
                )
            if "tone" in config_values:
                config_content = config_content.replace(
                    'tone: "casual and conversational"',
                    f'tone: "{config_values["tone"]}"'
                )
            if "language" in config_values:
                config_content = config_content.replace(
                    'language: "en"', f'language: "{config_values["language"]}"'
                )
            if "rss_feeds" in config_values:
                # Replace the example RSS feeds section
                feeds_yaml = "\n".join(f"    - {url}" for url in config_values["rss_feeds"])
                # Replace everything between "rss:" and the next section
                import re
                config_content = re.sub(
                    r"(  rss:\n)(    - https://example\.com/feed.*?)(\n\n)",
                    f"\\1{feeds_yaml}\n\n",
                    config_content,
                    flags=re.DOTALL,
                )
            if "github_repo" in config_values:
                repo = config_values["github_repo"]
                config_content = config_content.replace(
                    'github_repo: "username/my-podcast-feed"',
                    f'github_repo: "{repo}"'
                )
                owner_repo = repo.split("/")
                if len(owner_repo) == 2:
                    config_content = config_content.replace(
                        'github_pages_url: "https://username.github.io/my-podcast-feed"',
                        f'github_pages_url: "https://{owner_repo[0]}.github.io/{owner_repo[1]}"'
                    )

            with open(config_path, "w") as f:
                f.write(config_content)
        else:
            # Just copy the example
            with open(config_path, "w") as f:
                f.write(config_content)

        print(f"  Created: {config_path}")
    else:
        print(f"  Config already exists at: {config_path}")

    # =========================================================
    # Step 7: Create GitHub Pages repo
    # =========================================================
    if not args.skip_repo and config_values.get("github_repo") and gh_available:
        print("\n[7/7] Setting up GitHub Pages repository...")
        repo_name = config_values["github_repo"]

        # Check if repo already exists
        check = subprocess.run(
            ["gh", "repo", "view", repo_name],
            capture_output=True,
            text=True,
        )

        if check.returncode != 0:
            # Create the repo
            # Extract just the repo name (without owner) for creation
            repo_short = repo_name.split("/")[-1] if "/" in repo_name else repo_name
            result = subprocess.run(
                ["gh", "repo", "create", repo_short, "--private", "--clone"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                print(f"  Error creating repo: {result.stderr}")
                sys.exit(1)

            # Push initial commit with placeholder files
            import tempfile
            with tempfile.TemporaryDirectory() as tmp_dir:
                repo_dir = Path(tmp_dir) / repo_short

                # Clone the newly created repo
                subprocess.run(
                    ["gh", "repo", "clone", repo_name, str(repo_dir)],
                    capture_output=True,
                    text=True,
                )

                # Create episodes directory
                (repo_dir / "episodes").mkdir(exist_ok=True)
                (repo_dir / "episodes" / ".gitkeep").touch()

                # Create placeholder feed.xml
                feed_placeholder = textwrap.dedent(f"""\
                    <?xml version="1.0" encoding="UTF-8"?>
                    <rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
                      <channel>
                        <title>{config_values.get('show_name', 'My Podcast')}</title>
                        <description>Your personalized AI-generated podcast</description>
                        <language>en</language>
                      </channel>
                    </rss>
                """)
                with open(repo_dir / "feed.xml", "w") as f:
                    f.write(feed_placeholder)

                # Create index.html
                index_html = textwrap.dedent(f"""\
                    <!DOCTYPE html>
                    <html>
                    <head><title>{config_values.get('show_name', 'My Podcast')}</title></head>
                    <body>
                      <h1>{config_values.get('show_name', 'My Podcast')}</h1>
                      <p>Subscribe to this podcast by adding the RSS feed to your podcast player:</p>
                      <code>{config_values.get('github_pages_url', '')}/feed.xml</code>
                    </body>
                    </html>
                """)
                with open(repo_dir / "index.html", "w") as f:
                    f.write(index_html)

                # Create empty episodes.json
                with open(repo_dir / "episodes.json", "w") as f:
                    json.dump([], f)

                # Commit and push
                subprocess.run(["git", "add", "."], cwd=str(repo_dir), capture_output=True)
                subprocess.run(
                    ["git", "commit", "-m", "Initial setup for personalized podcast feed"],
                    cwd=str(repo_dir),
                    capture_output=True,
                )
                subprocess.run(["git", "push"], cwd=str(repo_dir), capture_output=True)

            # Enable GitHub Pages
            owner = repo_name.split("/")[0]
            repo = repo_name.split("/")[1]
            pages_result = subprocess.run(
                [
                    "gh", "api",
                    f"repos/{owner}/{repo}/pages",
                    "-X", "POST",
                    "-f", "build_type=legacy",
                    "-f", "source[branch]=main",
                    "-f", "source[path]=/",
                ],
                capture_output=True,
                text=True,
            )
            if pages_result.returncode == 0:
                print(f"  GitHub Pages enabled!")
            else:
                print(f"  Note: Couldn't auto-enable Pages: {pages_result.stderr}")
                print(f"  You may need to enable it manually at: https://github.com/{repo_name}/settings/pages")

            print(f"  Repo created: https://github.com/{repo_name}")
        else:
            print(f"  Repo already exists: {repo_name}")
    else:
        print("\n[7/7] Skipping GitHub repo setup (no repo name provided or --skip-repo)")

    # =========================================================
    # Done!
    # =========================================================
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print(f"\nData directory: {data_dir}")
    print(f"Config file:    {config_path}")
    print(f"API keys file:  {env_path}")
    print(f"\nNext steps:")
    print(f"  1. Add your API keys to {env_path}")
    print(f"  2. Customize {config_path} if needed")
    print(f"  3. Generate your first episode with your coding agent: /podcast <your content>")


if __name__ == "__main__":
    main()
