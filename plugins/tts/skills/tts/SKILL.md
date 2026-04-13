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

## Headless / SSH environments

On servers without audio output (headless, SSH, containers), the script automatically detects this and saves the audio to a temp file instead of trying to play it. The output will look like:

```
No audio output detected (headless/SSH). Audio saved to file.
FILE:/tmp/tts-abc123.mp3
```

When you see `FILE:` in the output, deliver the audio to the user through whatever channel is available (file server, chat attachment, email, etc.).

**Environment variables:**
- `TTS_FORCE_PLAY=1` — Force local playback even if no audio device is detected
- `TTS_NO_PLAY=1` — Force file output even on machines with audio

**Notes:**
- Requires internet connection (uses Microsoft's online TTS service)
- Dependencies: `pip install edge-tts pygame`
