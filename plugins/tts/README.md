# TTS Plugin for Claude Code

Text-to-speech plugin using [edge-tts](https://github.com/rany2/edge-tts) with chunked playback for low latency.

## Quick Start

**One-liner install (clone + deps):**

```bash
git clone https://github.com/pogohoper/Plugins-for-Claude.git && cd Plugins-for-Claude/plugins/tts && pip install -r requirements.txt
```

**Then run Claude Code with the plugin:**

```bash
claude --plugin-dir ./Plugins-for-Claude/plugins/tts
```

**Or use the install script:**

```bash
# macOS/Linux
./install.sh

# Windows
install.cmd
```

## Features

- **Low-latency chunked playback** — splits text at sentence boundaries and pre-generates the next chunk while the current one plays
- **Multiple voices** — Andrew (default), Guy, Aria, Ava, Jenny, Brian
- **Adjustable speech rate** — slow, normal, fast
- **File output** — optionally save audio to MP3 instead of playing

## Usage

Once installed, Claude will automatically use TTS when you ask it to speak or read text aloud. You can also invoke it directly:

```
/tts Hello, this is a test of the text to speech system.
```

### Voice options

| Voice   | ID                    |
|---------|-----------------------|
| andrew  | en-US-AndrewNeural    |
| guy     | en-US-GuyNeural       |
| aria    | en-US-AriaNeural      |
| ava     | en-US-AvaNeural       |
| jenny   | en-US-JennyNeural     |
| brian   | en-US-BrianNeural     |

### Scripts

- **`say.py`** — Quick speech with automatic chunking (default, used by `/tts`)
- **`speak.py`** — Full-featured with voice/rate/output options

## Requirements

- Python 3.10+
- Internet connection (edge-tts uses Microsoft's online TTS service)
- `edge-tts` and `pygame` (installed automatically by the install script)
