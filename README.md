# Personalized Podcast

A Claude Code skill that turns any content into a podcast episode. Give it text, point it at files, or describe a topic — it writes a two-host conversation script, generates audio with Fish Audio TTS, and publishes to your personal RSS feed. Subscribe once in your podcast app and new episodes show up automatically.

## How it works

```
You: /podcast read ~/Downloads/article.txt
          |
          v
    Claude reads the content
          |
          v
    Writes a script (two hosts riffing back and forth)
          |
          v
    Fish Audio turns each line into speech
          |
          v
    Stitches audio + publishes to GitHub Pages
          |
          v
    Episode appears in your podcast app
```

The show has two AI hosts:
- **Alex** — the curious one who introduces topics, asks questions, gets excited
- **Sam** — the analytical one who adds depth, offers opinions, drops the witty takes

They sound like two friends chatting over coffee, not news anchors reading teleprompters.

## Quick start

### 1. Install the skill

Clone into your Claude Code skills directory:

```bash
gh repo clone zarazhangrui/personalized-podcast-skill ~/.claude/skills/personalized-podcast
```

### 2. Set up Python environment

```bash
python3 -m venv ~/.claude/personalized-podcast/venv
~/.claude/personalized-podcast/venv/bin/pip install fish-audio-sdk pydub pyyaml python-dotenv jinja2 audioop-lts
```

You also need ffmpeg for audio processing:

```bash
brew install ffmpeg    # macOS
sudo apt install ffmpeg # Ubuntu
```

### 3. Get a Fish Audio API key

1. Create an account at [fish.audio](https://fish.audio)
2. Go to your profile/settings and copy your API key
3. Save it:

```bash
echo "FISH_API_KEY=your_key_here" > ~/.claude/personalized-podcast/.env
```

### 4. Pick voices

Browse [fish.audio/discovery](https://fish.audio/discovery/) and find two voices you like — one for each host. Copy their reference IDs.

### 5. Configure

```bash
cp ~/.claude/skills/personalized-podcast/config/config.example.yaml ~/.claude/personalized-podcast/config.yaml
```

Edit `~/.claude/personalized-podcast/config.yaml` and fill in:
- `show_name` — whatever you want your podcast called
- `host_a_voice_id` and `host_b_voice_id` — the Fish Audio reference IDs you picked
- `github_repo` — where your feed will be hosted (e.g., `yourusername/my-podcast-feed`)
- `github_pages_url` — the corresponding GitHub Pages URL

### 6. Create the feed repo

```bash
~/.claude/personalized-podcast/venv/bin/python ~/.claude/skills/personalized-podcast/scripts/bootstrap.py \
  --config-json '{"show_name": "Your Show Name", "github_repo": "yourusername/my-podcast-feed"}'
```

This creates a private GitHub repo with GitHub Pages enabled.

### 7. Subscribe

Add your feed URL to any podcast app:

| App | How to subscribe |
|-----|-----------------|
| Apple Podcasts | Library > menu (three dots) > Follow a Show by URL |
| Overcast | + button > Add URL |
| Pocket Casts | Search > Submit RSS Feed |
| Castro | Discover > Subscribe by URL |
| Snipd | Library > Add Podcast > Add by RSS Feed |

Your feed URL is: `https://yourusername.github.io/my-podcast-feed/feed.xml`

(Spotify doesn't support personal RSS feeds.)

## Usage

In Claude Code, just type:

```
/podcast Here's an article about...
```

or:

```
/podcast read ~/Downloads/newsletter.txt
```

or point to multiple files:

```
/podcast read ~/notes/meeting.txt and ~/notes/research.md
```

Claude reads the content, writes a script, asks you for an episode title, generates the audio, and publishes it to your feed.

## Architecture

```
~/.claude/skills/personalized-podcast/     # The skill (this repo)
  SKILL.md                                  # Skill instructions for Claude
  scripts/
    speak.py                                # Fish Audio TTS + audio stitching
    publish.py                              # Push episodes to GitHub Pages
    bootstrap.py                            # One-time repo setup
    utils.py                                # Config loading, logging, etc.
  templates/
    feed_template.xml                       # RSS feed Jinja template
  config/
    config.example.yaml                     # Example config to copy

~/.claude/personalized-podcast/            # Your data (not in this repo)
  config.yaml                               # Your config
  .env                                      # Your Fish Audio API key
  scripts_output/                           # Generated scripts (JSON)
  episodes/                                 # Generated MP3 files
  logs/                                     # Pipeline logs
```

## Tech stack

- **Script generation:** Claude itself (no separate LLM API call needed)
- **Text-to-speech:** [Fish Audio](https://fish.audio) — 2M+ voices, simple SDK
- **Audio processing:** pydub + ffmpeg
- **Feed hosting:** GitHub Pages (private repo, public URL)
- **Feed format:** RSS 2.0 with iTunes podcast extensions

## Troubleshooting

| Error | Fix |
|-------|-----|
| "API key not found" | Check `~/.claude/personalized-podcast/.env` has a valid `FISH_API_KEY` |
| "No voice ID set" | Browse fish.audio/discovery, pick voices, add IDs to config.yaml |
| "ffmpeg not installed" | `brew install ffmpeg` |
| "gh not authenticated" | `gh auth login` |
| TTS quota exceeded | Fish Audio free tier has limits. Wait for reset or upgrade your plan |
