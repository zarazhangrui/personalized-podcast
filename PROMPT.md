# Podcast Script Prompt

This file controls how your podcast scripts are written. Edit it to change the hosts, the format, the tone, or create entirely new show formats.

## Hosts

The show has two hosts:

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

## Ideas for alternative formats

You can completely rewrite this file to create different show styles. Some ideas:

**Solo narrator:** One host walks through the content in a thoughtful monologue. Use only speaker "A".

**Debate:** Two hosts take opposing sides on the topic. One is bullish, the other is skeptical. They challenge each other.

**Eavesdrop:** Two hosts discuss a person (based on transcripts, writing, or other personal content) as if that person isn't in the room. They share observations about personality, communication patterns, and decision-making.

**Interview:** One host plays the interviewer, the other plays an expert being interviewed about the topic.

**News roundup:** Hosts go through a list of items (tweets, headlines, bullet points) one by one. Each item is read aloud, then discussed briefly before moving to the next.
