---
name: podcast
description: Generate a podcast episode from content you provide. Paste text, point to local files, or describe a topic - Claude writes a two-host conversation script, generates audio with Fish Audio TTS, and plays it for you.
---

# Personalized Podcast

Turn any content into a podcast episode with two engaging hosts who discuss it in a casual, conversational style.

## First-time setup

If `~/.claude/personalized-podcast/config.yaml` does not exist, run through this setup BEFORE doing anything else. Do each step yourself - don't ask the user to run commands.

### Step 1: Install dependencies

```bash
# Create data directory and venv
mkdir -p ~/.claude/personalized-podcast/{scripts_output,episodes,logs}
python3 -m venv ~/.claude/personalized-podcast/venv

# Install Python packages
~/.claude/personalized-podcast/venv/bin/pip install fish-audio-sdk pydub pyyaml python-dotenv jinja2 audioop-lts
```

Check ffmpeg is installed:
```bash
ffmpeg -version
```
If not found, install it: `brew install ffmpeg` (macOS) or `sudo apt install ffmpeg` (Linux).

### Step 2: Create config with default voices

```bash
cp ~/.claude/skills/personalized-podcast/config/config.example.yaml ~/.claude/personalized-podcast/config.yaml
```

The config comes with two pre-picked voices that work out of the box. No voice selection needed for first use.

### Step 3: Get Fish Audio API key

Ask the user: "To generate audio, you'll need a free Fish Audio API key. Here's how to get one:"

1. Go to fish.audio and create an account (free)
2. Go to your profile/settings and copy your API key

Then create the .env file and open it for them:

```bash
echo "FISH_API_KEY=your_key_here" > ~/.claude/personalized-podcast/.env
open ~/.claude/personalized-podcast/.env
```

Tell them: "Paste your Fish Audio API key in this file, replacing 'your_key_here'. Save and close."

IMPORTANT: Never ask the user to paste API keys in the chat. Always use the .env file.

### Step 4: Done

Tell the user: "Setup complete! Type /podcast followed by any content to generate your first episode."

Do NOT set up RSS or GitHub Pages during first-time setup. That's optional and comes later.

---

## Generating an episode

### Step 1: Read the content

Read all the content the user provided. If they pointed to files, read them with the Read tool. If they pasted a URL, fetch it. Combine everything into your understanding of the source material.

### Step 2: Write the podcast script

Read the prompt file at `~/.claude/skills/personalized-podcast/PROMPT.md` for the hosts, style, structure, and output format. Follow those instructions to write the script.

If the user included custom instructions in their `/podcast` message (e.g., "make it a debate" or "hosts should eavesdrop on my conversation"), incorporate those. The user's inline instructions override PROMPT.md for that episode.

Save the script as a JSON array using the Write tool to: `~/.claude/personalized-podcast/scripts_output/YYYY-MM-DD.json` (use today's date). If a file for today already exists, append a number (e.g., `2026-04-05-2.json`).

### Step 3: Generate audio

Run the speak script:

```bash
~/.claude/personalized-podcast/venv/bin/python ~/.claude/skills/personalized-podcast/scripts/speak.py --script <path_to_script.json>
```

This outputs the path to the generated MP3 file.

### Step 4: Play the audio

IMMEDIATELY open the audio file for the user:

```bash
open <path_to_mp3>
```

On Linux use `xdg-open` instead of `open`.

### Step 5: Post-generation tips

After the audio plays, tell the user:

> "Your podcast episode is ready! Here are some things you can customize:
>
> **Customize the script prompt:** The default show is two hosts having a casual conversation, but you can change it to anything. Edit `PROMPT.md` to create your own format. Some ideas:
> - **Debate** - two hosts take opposing sides and challenge each other
> - **Eavesdrop** - two hosts discuss a person (from transcripts or personal content) as if they're not in the room, sharing observations about personality and communication patterns
> - **Interview** - one host interviews the other as an expert on the topic
> - **Solo narrator** - one voice walks through the content as a monologue
> - **News roundup** - hosts go through a list of items one by one, reading each aloud then discussing
>
> Or just describe the format you want inline when you run `/podcast` (e.g., "/podcast make it a debate about this article") and I'll follow your instructions for that episode.
>
> **Pick your own voices:** Browse voices at https://fish.audio/discovery, find two you like, copy their reference IDs, and update `~/.claude/personalized-podcast/config.yaml` under `host_a_voice_id` and `host_b_voice_id`.
>
> **Customize the show:** Edit the `show_name` and `tone` in your config file to change the podcast's personality.
>
> **Set up an RSS feed:** Want episodes delivered to your podcast app (Apple Podcasts, Spotify, Overcast, Snipd, etc.) automatically? I can set up a personal RSS feed for you. Just ask!"

Only show these tips the FIRST time, or if the user asks about customization.

## RSS feed setup (only when user asks)

When the user wants to set up an RSS feed, walk them through these steps:

### 1. Create a public GitHub repo

```bash
gh repo create USERNAME/podcast-feed --public --description "Personal podcast feed"
```

Replace USERNAME with their GitHub username.

### 2. Enable GitHub Pages

```bash
# Clone, add initial files, push
cd /tmp && mkdir podcast-feed && cd podcast-feed && git init
echo '[]' > episodes.json
# Generate an initial empty feed.xml using the template
```

Then enable GitHub Pages:
```bash
gh api repos/USERNAME/podcast-feed/pages -X POST --input - << 'EOF'
{"source":{"branch":"main","path":"/"},"build_type":"legacy"}
EOF
```

### 3. Update config

Update `~/.claude/personalized-podcast/config.yaml` with:
```yaml
publish:
  github_repo: "USERNAME/podcast-feed"
  base_url: "https://USERNAME.github.io/podcast-feed"
```

### 4. Subscribe in a podcast app

Give the user their feed URL and instructions:

| App | How to subscribe |
|-----|-----------------|
| Apple Podcasts (Mac) | Menu bar: File > Add a Show by URL |
| Apple Podcasts (iPhone) | Library > Edit (top right) > Add a Show by URL |
| Overcast | "+" (top right) > Add URL |
| Pocket Casts | Discover tab > paste URL in search bar > Subscribe |
| Castro | Search tab > paste URL in search bar > Add Podcast |
| Snipd | Home > Podcasts > three-dot menu (top right) > Add RSS |
| Spotify | See Spotify instructions below |

Feed URL: `https://USERNAME.github.io/podcast-feed/feed.xml`

**Spotify setup (one-time, takes 24-48 hours for approval):**

IMPORTANT: Before proceeding, warn the user: "Heads up - submitting to Spotify makes your podcast **public**. Anyone on Spotify can find and listen to it. The other apps above (Apple Podcasts, Overcast, etc.) are private - only people you share the RSS URL with can find your show. Want to proceed with Spotify?"

If they want to proceed:
1. Make sure `owner_email` is set in config.yaml. If not, ask for their email and add it.
2. Go to [podcasters.spotify.com](https://podcasters.spotify.com) and sign in
3. Click "Add existing podcast"
4. Paste your feed URL
5. Spotify sends a verification email - click to verify
6. Your show appears on Spotify within 24-48 hours

### 5. Publish episodes

After the RSS feed is set up, future episodes can be published with:

```bash
~/.claude/personalized-podcast/venv/bin/python ~/.claude/skills/personalized-podcast/scripts/publish.py --mp3 <path_to_mp3> --title "<title>" --description "<description>"
```

## Troubleshooting

- **"API key not found"** - Check ~/.claude/personalized-podcast/.env has a valid FISH_API_KEY
- **"ffmpeg not installed"** - Run: `brew install ffmpeg` (macOS) or `sudo apt install ffmpeg` (Linux)
- **"gh not authenticated"** - Run: `gh auth login`
- **TTS quota exceeded** - Fish Audio free tier has monthly limits. Wait for reset or upgrade your plan.
