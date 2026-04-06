# Personalized Podcast

**NotebookLM-style AI podcasts, except you control everything.**

The script. The prompt. The hosts' roles. Their voices. The content they discuss. All of it.

A coding agent skill that turns any content into a two-host podcast episode. Paste in text, point it at files, drop a URL. Two AI hosts read your content and have a natural conversation about it. You get an MP3 that plays immediately. Set up an RSS feed and listen in the apps you already use: Apple Podcasts, Spotify, Overcast, Snipd, Pocket Casts. No new app to download.

## Why this exists

**Turn anything into a podcast you can listen to on the go.** Newsletters, long reads, tweets, research papers, meeting notes. Instead of reading on a screen, you listen to two people break it down while you walk, commute, or cook. Set up the RSS feed once and new episodes show up right where you already listen to podcasts.

**Know yourself from the outside.** This is the unexpected use case. Feed it personal content: your resume, meeting transcripts, journal entries, even your browser history. Then ask the hosts to comment on their impressions of you. What patterns do they see in how you think, communicate, make decisions? It is genuinely illuminating to hear two voices discuss you as if you're not in the room.

## Quick start

### 1. Install

```bash
gh repo clone zarazhangrui/personalized-podcast-skill ~/.claude/skills/personalized-podcast
```

### 2. Go

```
/podcast <paste content, point to files, or describe a topic>
```

That's it. On first run, Claude sets up the Python environment, installs dependencies, and asks you for a free [Fish Audio](https://fish.audio) API key. Default voices are pre-configured. Your first episode generates immediately.

## What you can do with it

**Consume content as audio**
```
/podcast read ~/Downloads/newsletter.txt
/podcast https://some-article-url.com
/podcast Here's a thread about AI agents I want to hear discussed...
```

**Self-reflection**
```
/podcast read ~/Documents/my-resume.pdf and have the hosts analyze my career trajectory
/podcast read ~/transcripts/meeting.txt and have the hosts eavesdrop and share their impressions of me
```

**Custom formats**
```
/podcast read ~/notes.md, make it a debate between an optimist and a skeptic
/podcast read these 3 files, hosts should focus on what's surprising or counterintuitive
```

You can change the prompt, the hosts' personalities, the episode length, the tone. It is all in your config file.

## How it works

```
/podcast <your content>
        |
        v
  Claude reads the content and writes a two-host conversation script
        |
        v
  Fish Audio generates speech for each line (different voice per host)
        |
        v
  Audio gets stitched together with natural pacing
        |
        v
  MP3 opens and plays on your computer
```

The default show has two hosts:
- **Alex** (Speaker A): The curious one. Introduces topics, asks questions, gets excited.
- **Sam** (Speaker B): The analytical one. Adds depth, offers opinions, drops the witty takes.

They sound like two friends talking over coffee. Not news anchors. Not a lecture.

## Make it yours

**Pick your own voices.** Browse [fish.audio/discovery](https://fish.audio/discovery/). Find voices you like. Copy their reference IDs into your config. You can make your hosts sound however you want.

**Change the show's personality.** Edit `show_name` and `tone` in `~/.claude/personalized-podcast/config.yaml`. Make it serious, funny, academic, casual, confrontational. Up to you.

**Customize the script prompt.** The instructions for how the hosts behave live in `SKILL.md`. You can edit them to change the format entirely: make it a solo narrator, a three-person panel, a debate, an interview.

**Set up an RSS feed.** Want episodes delivered to your podcast app automatically? Just ask Claude: "Set up an RSS feed for my podcast." It creates a GitHub Pages feed you can subscribe to in Apple Podcasts, Overcast, Pocket Casts, Snipd, Spotify, or any podcast app that supports RSS.

## Requirements

- A coding agent that supports skills (e.g. Claude Code, Gemini CLI, Copilot CLI)
- Python 3.10+
- ffmpeg (`brew install ffmpeg` on macOS)
- [Fish Audio](https://fish.audio) account (free tier available)

## About

Built by [Zara Zhang](https://x.com/zarazhangrui). Your AI coding agent already understands context, writes well, and follows instructions. Why not have it write you a podcast script, generate the audio, and deliver it to your ears?

The entire pipeline runs locally through your coding agent. No separate backend. No hosted service. No subscription. Just a skill that turns your coding agent into a podcast producer.

## Under the hood

```
~/.claude/skills/personalized-podcast/     # The skill (this repo)
  SKILL.md                                  # Instructions for the coding agent
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

**Script generation:** Your coding agent writes the script directly. No separate LLM API call needed.

**Text-to-speech:** [Fish Audio](https://fish.audio) with 2M+ voices and a free tier.

**Audio processing:** pydub + ffmpeg for stitching segments with natural pauses and fade effects.

**Feed hosting (optional):** GitHub Pages, auto-deploys on every push.
