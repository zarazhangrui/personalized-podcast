---
name: podcast
description: Generate a podcast episode from content you provide. Paste text, point to local files, or describe a topic — Claude writes a two-host conversation script, generates audio with Fish Audio, and publishes to your podcast feed.
---

# Personalized Podcast

Turn any content into a podcast episode with two engaging hosts who discuss it in a casual, conversational style. The episode is published to your personal RSS feed, playable in any podcast app.

## How to use

The user provides content in one of these ways:
- **Pasted text:** The user pastes article text, notes, or any content directly after `/podcast`
- **File paths:** The user says something like "read ~/Downloads/article.txt" — use the Read tool to read those files
- **Both:** A mix of pasted text and file references

## What to do

### Step 1: Read the content

Read all the content the user provided. If they pointed to files, read them with the Read tool. Combine everything into your understanding of the source material.

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

**Output format:** A JSON array where each element has "speaker" (either "A" or "B") and "text" (what they say):

```json
[
  {"speaker": "A", "text": "Hey everyone, welcome back to Made for Zara..."},
  {"speaker": "B", "text": "Yeah, so today we've got some really interesting stuff..."}
]
```

Save the script to a file using the Write tool. Save it to: `~/.claude/personalized-podcast/scripts_output/YYYY-MM-DD.json` (use today's date).

### Step 2.5: Ask for the episode title

Ask the user what they'd like to title this episode. Suggest a short, descriptive title based on the content (e.g., "Permissionless Leverage in the AI Age" or "Why Grad School Might Not Be Worth It"). The user can accept your suggestion or provide their own. Remember this title for Step 4.

### Step 3: Generate audio

Run the speak script to convert the script to audio:

```bash
~/.claude/personalized-podcast/venv/bin/python ~/.claude/skills/personalized-podcast/scripts/speak.py --script ~/.claude/personalized-podcast/scripts_output/YYYY-MM-DD.json
```

Replace YYYY-MM-DD with today's date. This will output the path to the generated MP3 file. Note this path for the next step.

If it fails with a quota error, tell the user and suggest retrying later with:
```bash
~/.claude/personalized-podcast/venv/bin/python ~/.claude/skills/personalized-podcast/scripts/speak.py --script <path_to_script.json>
```

### Step 4: Publish to feed

Run the publish script with the MP3 path from step 3 and the episode title from step 2.5:

```bash
~/.claude/personalized-podcast/venv/bin/python ~/.claude/skills/personalized-podcast/scripts/publish.py --mp3 <path_to_mp3> --title "<episode_title>" --description "<short_description>"
```

### Step 5: Confirm

Tell the user the episode is live. Remind them of their feed URL:
> "New episode published! It will appear in your podcast app shortly."
> "Feed URL: https://made-for-zara.vercel.app/feed.xml"

## First-time setup

If the user hasn't set up yet (no config.yaml or .env file exists), walk them through these steps:

### 1. Fish Audio API key

1. Go to fish.audio and create an account
2. Go to your profile/settings and find your API key
3. Create the .env file and open it for the user:

```bash
echo "FISH_API_KEY=your_key_here" > ~/.claude/personalized-podcast/.env
open ~/.claude/personalized-podcast/.env
```

Tell the user: "Please paste your Fish Audio API key in this file, replacing 'your_key_here'."

IMPORTANT: Never ask the user to paste API keys in the chat. Always use the .env file.

### 2. Voice selection

Help the user pick two voices:

> "Fish Audio has millions of voices. Browse them at fish.audio/discovery. Pick one male and one female voice for contrast. When you find a voice you like, copy its reference ID from the URL or the voice page."

Once they have two voice IDs, update config.yaml:

```bash
open ~/.claude/personalized-podcast/config.yaml
```

Tell them to paste the IDs into `host_a_voice_id` and `host_b_voice_id`.

### 3. GitHub repo (if not already set up)

Run the bootstrap script:

```bash
~/.claude/personalized-podcast/venv/bin/python ~/.claude/skills/personalized-podcast/scripts/bootstrap.py --config-json '{"show_name": "SHOW_NAME", "github_repo": "USERNAME/REPO_NAME"}'
```

### 4. Subscribe

Give the user their feed URL and instructions for their podcast player (Apple Podcasts: Library → Follow a Show by URL; Overcast: + → Add URL; Pocket Casts: Search → Submit RSS Feed).

## Troubleshooting

- **"API key not found"** — Check ~/.claude/personalized-podcast/.env has a valid FISH_API_KEY
- **"No voice ID set"** — Browse fish.audio/discovery, pick voices, add IDs to config.yaml
- **"ffmpeg not installed"** — Run: `brew install ffmpeg`
- **"gh not authenticated"** — Run: `gh auth login`
- **TTS quota exceeded** — Fish Audio free tier has limits. Wait for reset or upgrade. Retry with the speak command above.
