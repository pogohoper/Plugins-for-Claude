---
name: tts
description: Text-to-speech synthesis using edge-tts. Use when the user asks Claude to speak, say something out loud, read text aloud, convert text to speech, or generate audio from text. Also use when asked to "use TTS" or "speak this".
user-invocable: true
argument-hint: "<text to speak>"
allowed-tools:
  - Bash
---

# TTS

Speak text aloud using chunked playback for low latency. Long text is automatically split at sentence boundaries and the next chunk is pre-generated while the current one plays, so speech starts fast and plays seamlessly.

## Quick usage

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tts.py "$ARGUMENTS"
```

## With options

```bash
# Choose a voice
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tts.py "Hello world" --voice aria

# Speak faster
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tts.py "Hello world" --rate fast

# Save to file instead of playing
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tts.py "Hello world" --output speech.mp3

# List voices
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tts.py --list-voices

# Pipe text in
echo "Hello world" | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tts.py
```

**Voices:** andrew (default), guy, aria, ava, jenny, brian

**Rates:** slow, normal (default), fast

**Notes:**
- Requires internet connection (uses Microsoft's online TTS service)
- Dependencies: `pip install edge-tts pygame`
