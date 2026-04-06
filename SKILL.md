---
name: podcast
description: Generate a podcast episode from content you provide. Paste text, point to local files, or describe a topic. Two AI hosts discuss it in a natural conversation. Listen locally or in your favorite podcast app via RSS.
---

# Personalized Podcast

When the user invokes this skill, start by introducing it:

> "This skill turns any content into a podcast episode with two AI hosts who discuss it in a natural, conversational style. Think NotebookLM, but you control everything: the script prompt, the hosts' voices, the show format.
>
> You can use it to:
> - **Listen to anything on the go.** Paste an article, point to a file, drop a URL. Instead of reading, you get two people breaking it down while you walk, commute, or cook.
> - **Understand yourself from the outside.** Feed it personal content like meeting transcripts, your resume, or journal entries, and have the hosts share their impressions of you. It's genuinely illuminating.
> - **Create your own show.** Set up an RSS feed and new episodes show up in the podcast app you already use (Apple Podcasts, Spotify, Overcast, Snipd). No new app to download.
>
> Let's get started. What content do you want to turn into a podcast?"

If the user already provided content with their `/podcast` command, skip the question and go straight to setup check.

---

## First-time setup

If `~/.claude/personalized-podcast/config.yaml` does not exist, run through this setup BEFORE generating. Do each step yourself - don't ask the user to run commands.

### Step 1: Install dependencies

```bash
mkdir -p ~/.claude/personalized-podcast/{scripts_output,episodes,logs}
python3 -m venv ~/.claude/personalized-podcast/venv
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

Tell the user:

> "To turn your script into audio, this skill uses Fish Audio for text-to-speech. They have a free tier with 2 million+ voices. You just need an API key:
>
> 1. Go to https://fish.audio and create a free account
> 2. Go to https://fish.audio/app/api-keys/ and create an API key"

Then create the .env file and open it:

```bash
echo "FISH_API_KEY=your_key_here" > ~/.claude/personalized-podcast/.env
open ~/.claude/personalized-podcast/.env
```

Tell them: "Paste your Fish Audio API key in this file, replacing 'your_key_here'. Save and close."

IMPORTANT: Never ask the user to paste API keys in the chat. Always use the .env file.

### Step 4: Done

Tell the user:

> "You're all set! The default show has two hosts - Alex (curious, energetic) and Sam (analytical, witty) - with voices pre-configured. Let's generate your first episode."

Then proceed to generate the episode. Do NOT set up RSS or GitHub Pages during first-time setup. That's optional and comes later.

---

## Generating an episode

### Step 1: Read the content

Read all the content the user provided. If they pointed to files, read them with the Read tool. If they pasted a URL, fetch it. Combine everything into your understanding of the source material.

### Step 2: Write the podcast script

Read the prompt file at `~/.claude/skills/personalized-podcast/PROMPT.md` for the hosts, style, structure, and output format. Follow those instructions to write the script.

If the user included custom instructions in their `/podcast` message (e.g., "make it a debate" or "hosts should eavesdrop on my conversation"), incorporate those. The user's inline instructions override PROMPT.md for that episode.

Save the script as a JSON array using the Write tool to: `~/.claude/personalized-podcast/scripts_output/YYYY-MM-DD.json` (use today's date). If a file for today already exists, append a number (e.g., `2026-04-05-2.json`).

### Step 3: Generate audio

Tell the user: "Script written. Now generating audio - this takes about a minute depending on episode length."

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

> "Your episode is ready! A few things you can do from here:
>
> **Try different show formats.** The default is two hosts chatting, but you can do anything. Just describe it when you run `/podcast`:
> - "/podcast make it a debate about this article"
> - "/podcast hosts should eavesdrop on my conversation and share their impressions of me"
> - "/podcast interview format, one host asks questions and the other is the expert"
> - "/podcast solo narrator, walk me through this research paper"
> - "/podcast news roundup, read each tweet aloud then discuss"
>
> Or edit `PROMPT.md` to permanently change your show's format.
>
> **Pick your own voices.** The default voices are solid, but Fish Audio has 2 million+ to choose from. Browse https://fish.audio/discovery, find two you like, and update the voice IDs in `~/.claude/personalized-podcast/config.yaml`.
>
> **Listen in your podcast app.** Want new episodes delivered to Apple Podcasts, Spotify, Overcast, or Snipd automatically? Just ask me to set up an RSS feed for you - takes about a minute."

Only show these tips the FIRST time, or if the user asks about customization.

---

## RSS feed setup (only when user asks)

When the user wants to set up an RSS feed, explain why it's useful:

> "This creates a personal podcast feed that works in any podcast app. Once it's set up, every time you generate a new episode, it gets published to the feed and shows up where you already listen to podcasts. No new app needed."

Then walk them through these steps:

### 1. Create a public GitHub repo

Ask for their GitHub username, then:

```bash
gh repo create USERNAME/podcast-feed --public --description "Personal podcast feed"
```

### 2. Enable GitHub Pages

```bash
cd /tmp && mkdir podcast-feed && cd podcast-feed && git init
echo '[]' > episodes.json
```

Generate an initial empty feed.xml using the template, then push and enable GitHub Pages:

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

Tell the user their feed URL and give them the steps for their preferred app:

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

IMPORTANT: Before proceeding, warn the user: "Heads up - submitting to Spotify makes your podcast **public**. Anyone on Spotify can find and listen to it. The other apps above are private - only people you share the RSS URL with can find your show. Want to proceed with Spotify?"

If they want to proceed:
1. Make sure `owner_email` is set in config.yaml. If not, ask for their email and add it.
2. Go to [podcasters.spotify.com](https://podcasters.spotify.com) and sign in
3. Click "Add existing podcast"
4. Paste the feed URL
5. Spotify sends a verification email - click to verify
6. The show appears on Spotify within 24-48 hours

### 5. Publish episodes

After the RSS feed is set up, future episodes can be published with:

```bash
~/.claude/personalized-podcast/venv/bin/python ~/.claude/skills/personalized-podcast/scripts/publish.py --mp3 <path_to_mp3> --title "<title>" --description "<description>"
```

---

## Troubleshooting

- **"API key not found"** - Check ~/.claude/personalized-podcast/.env has a valid FISH_API_KEY
- **"ffmpeg not installed"** - Run: `brew install ffmpeg` (macOS) or `sudo apt install ffmpeg` (Linux)
- **"gh not authenticated"** - Run: `gh auth login`
- **TTS quota exceeded** - Fish Audio free tier has monthly limits. Wait for reset or upgrade your plan.
