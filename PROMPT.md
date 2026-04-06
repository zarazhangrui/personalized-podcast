# Podcast Script Prompt

Write a podcast script as a JSON array. The show has two hosts:

- **Alex (Speaker A):** The curious one who introduces topics and asks insightful questions. Energetic and enthusiastic.
- **Sam (Speaker B):** The analytical one who dives deeper, adds context, and offers opinions. Thoughtful and witty.

## Style

- Sound like two friends chatting, not news anchors reading teleprompters
- Use contractions, incomplete sentences, and natural speech patterns
- Include reactions: "Wait, really?", "That's wild", "Okay so here's the thing..."
- Have genuine opinions - it's okay to be skeptical or excited about something
- Avoid jargon dumps - if a technical concept comes up, explain it briefly and naturally
- Each speaker turn should be 1-4 sentences (not long monologues)
- Target approximately 1,500 words total (roughly 10 minutes of speech)

## Structure

1. **Opening** (~30 seconds): Alex opens with a brief, energetic teaser of what's coming. Sam jumps in with a quick reaction.
2. **Main discussion** (~8 minutes): Go through the content. One host introduces a point conversationally, the other reacts, asks questions, or adds context. Use natural transitions between topics.
3. **Closing** (~30 seconds): Quick wrap-up. Sam highlights the biggest takeaway. Alex signs off.

## Output format

A JSON array where each element has "speaker" (either "A" or "B") and "text":

```json
[
  {"speaker": "A", "text": "Hey everyone, welcome back..."},
  {"speaker": "B", "text": "Yeah, so today we've got some really interesting stuff..."}
]
```
