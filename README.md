# Personalized Podcast

A Claude Code skill that turns any content into a podcast episode. Give it text, point it at files, or describe a topic — it writes a two-host conversation script, generates audio, and plays it for you.

## Demo

```
You: /podcast Here's an article about AI coding assistants getting really good...

Claude: [reads content, writes script, generates audio]
        Playing your episode now! (7:11, two hosts discussing AI coding)
```

## Quick start

### 1. Install the skill

```bash
gh repo clone zarazhangrui/personalized-podcast-skill ~/.claude/skills/personalized-podcast
```

### 2. Use it

```
/podcast <paste content, point to files, or describe a topic>
```

That's it. On first run, Claude will automatically set up the Python environment, install dependencies, and ask you for a free [Fish Audio](https://fish.audio) API key. Default voices are pre-configured — your first episode generates immediately.

## What it does

```
/podcast <your content>
        |
        v
  Claude writes a script (two hosts riffing back and forth)
        |
        v
  Fish Audio turns each line into speech
        |
        v
  Audio file opens and plays on your computer
```

The show has two AI hosts:
- **Alex** — the curious one who introduces topics, asks questions, gets excited
- **Sam** — the analytical one who adds depth, offers opinions, drops the witty takes

They sound like two friends chatting over coffee, not news anchors reading teleprompters.

## Customize

**Pick your own voices:** Browse [fish.audio/discovery](https://fish.audio/discovery/), find voices you like, and update `~/.claude/personalized-podcast/config.yaml` with the reference IDs.

**Change the show's personality:** Edit `show_name` and `tone` in your config file.

**Set up an RSS feed:** Want episodes delivered to your podcast app? Ask Claude: "Set up an RSS feed for my podcast." It will create a GitHub Pages feed you can subscribe to in Apple Podcasts, Overcast, Pocket Casts, Snipd, or any podcast app.

## Requirements

- [Claude Code](https://claude.ai/code) (CLI, desktop app, or IDE extension)
- Python 3.10+
- ffmpeg (`brew install ffmpeg` on macOS)
- [Fish Audio](https://fish.audio) account (free tier available)

## How it works under the hood

```
~/.claude/skills/personalized-podcast/     # The skill (this repo)
  SKILL.md                                  # Instructions for Claude
  scripts/
    speak.py                                # Fish Audio TTS + audio stitching
    publish.py                              # Push episodes to GitHub Pages (optional)
    bootstrap.py                            # One-time repo setup (optional)
    utils.py                                # Config, logging, .env loading
  templates/
    feed_template.xml                       # RSS feed template (optional)
  config/
    config.example.yaml                     # Default config with pre-picked voices

~/.claude/personalized-podcast/            # Your data (created automatically)
  config.yaml                               # Your config
  .env                                      # Your Fish Audio API key
  scripts_output/                           # Generated scripts (JSON)
  episodes/                                 # Generated MP3 files
```

**Script generation:** Claude writes the script directly — no separate LLM API call needed.

**Text-to-speech:** [Fish Audio](https://fish.audio) — 2M+ voices, free tier, simple SDK.

**Audio processing:** pydub + ffmpeg for stitching and fade effects.

**Feed hosting (optional):** GitHub Pages with auto-deploy on push.
