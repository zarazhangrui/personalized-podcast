---
name: podcast
description: Generate a podcast episode from content you provide. Paste text, point to local files, or describe a topic — Claude writes a two-host conversation script, generates audio with Fish Audio TTS, and plays it for you.
---

# Personalized Podcast

Turn any content into a podcast episode with two engaging hosts who discuss it in a casual, conversational style.

## First-time setup

If `~/.claude/personalized-podcast/config.yaml` does not exist, run through this setup BEFORE doing anything else. Do each step yourself — don't ask the user to run commands.

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

Write a podcast script as a JSON array. The show has two hosts:

- **Alex (Speaker A):** The curious one who introduces topics and asks insightful questions. Energetic and enthusiastic.
- **Sam (Speaker B):** The analytical one who dives deeper, adds context, and offers opinions. Thoughtful and witty.

**Style guidelines:**
- Sound like two friends chatting, not news anchors reading teleprompters
- Use contractions, incomplete sentences, and natural speech patterns
- Include reactions: "Wait, really?", "That's wild", "Okay so here's the thing..."
- Have genuine opinions — it's okay to be skeptical or excited about something
- Avoid jargon dumps — if a technical concept comes up, explain it briefly and naturally
- Each speaker turn should be 1-4 sentences (not long monologues)
- Target approximately 1,500 words total (roughly 10 minutes of speech)

**Structure:**
1. **Opening** (~30 seconds): Alex opens with a brief, energetic teaser of what's coming. Sam jumps in with a quick reaction.
2. **Main discussion** (~8 minutes): Go through the content. One host introduces a point conversationally, the other reacts, asks questions, or adds context. Use natural transitions between topics.
3. **Closing** (~30 seconds): Quick wrap-up. Sam highlights the biggest takeaway. Alex signs off.

**Output format:** A JSON array where each element has "speaker" (either "A" or "B") and "text":

```json
[
  {"speaker": "A", "text": "Hey everyone, welcome back..."},
  {"speaker": "B", "text": "Yeah, so today we've got some really interesting stuff..."}
]
```

Save the script using the Write tool to: `~/.claude/personalized-podcast/scripts_output/YYYY-MM-DD.json` (use today's date). If a file for today already exists, append a number (e.g., `2026-04-05-2.json`).

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
> **Pick your own voices:** Browse voices at https://fish.audio/discovery — find two you like, copy their reference IDs, and update `~/.claude/personalized-podcast/config.yaml` under `host_a_voice_id` and `host_b_voice_id`.
>
> **Customize the show:** Edit the `show_name` and `tone` in your config file to change the podcast's personality.
>
> **Set up an RSS feed:** Want episodes delivered to your podcast app automatically? I can set up a personal RSS feed for you — just ask!"

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
| Overcast | + button > Add URL |
| Pocket Casts | Search > Submit RSS Feed |
| Castro | Discover > Subscribe by URL |
| Snipd | Library > Add Podcast > Add by RSS Feed |

Feed URL: `https://USERNAME.github.io/podcast-feed/feed.xml`

(Spotify doesn't support personal RSS feeds.)

### 5. Publish episodes

After the RSS feed is set up, future episodes can be published with:

```bash
~/.claude/personalized-podcast/venv/bin/python ~/.claude/skills/personalized-podcast/scripts/publish.py --mp3 <path_to_mp3> --title "<title>" --description "<description>"
```

## Troubleshooting

- **"API key not found"** — Check ~/.claude/personalized-podcast/.env has a valid FISH_API_KEY
- **"ffmpeg not installed"** — Run: `brew install ffmpeg` (macOS) or `sudo apt install ffmpeg` (Linux)
- **"gh not authenticated"** — Run: `gh auth login`
- **TTS quota exceeded** — Fish Audio free tier has monthly limits. Wait for reset or upgrade your plan.
