---
name: tts
description: Text-to-speech synthesis using edge-tts. Use when the user asks Claude to speak, say something out loud, read text aloud, convert text to speech, or generate audio from text. Also use when asked to "use TTS" or "speak this".
user-invocable: true
argument-hint: "<text to speak>"
allowed-tools:
  - Bash
---

# TTS

Speak text aloud using chunked playback for low latency:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/say.py "$ARGUMENTS"
```

Speak with voice/rate options:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/speak.py "Your text here" --voice andrew --rate normal
```

List available voices:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/speak.py --list-voices
```

**Available voices:** andrew (default), guy, aria, ava, jenny, brian

**Speech rates:** slow, normal (default), fast

**Notes:**
- Long text is automatically chunked by sentence for low latency
- User cannot interrupt playback
- Requires internet connection
- Dependencies: `pip install edge-tts pygame`
