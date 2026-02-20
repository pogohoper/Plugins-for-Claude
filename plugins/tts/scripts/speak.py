#!/usr/bin/env python3
"""TTS skill script - Speak text using edge-tts with voice and rate options."""

import argparse
import asyncio
import sys
import tempfile
import time
import os

try:
    import edge_tts
except ImportError:
    print("ERROR: edge-tts not installed. Run: pip install edge-tts")
    sys.exit(1)

try:
    import pygame
except ImportError:
    print("ERROR: pygame not installed. Run: pip install pygame")
    sys.exit(1)


DEFAULT_VOICE = "en-US-AndrewNeural"

VOICE_SHORTCUTS = {
    "andrew": "en-US-AndrewNeural",
    "guy": "en-US-GuyNeural",
    "aria": "en-US-AriaNeural",
    "ava": "en-US-AvaNeural",
    "jenny": "en-US-JennyNeural",
    "brian": "en-US-BrianNeural",
}

RATE_MAP = {
    "slow": "-20%",
    "normal": "+0%",
    "fast": "+25%",
}


async def generate_speech(text: str, voice: str, rate: str, output_path: str) -> None:
    """Generate speech from text using edge-tts."""
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)


def play_audio(file_path: str) -> None:
    """Play audio file using pygame."""
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.quit()


def main():
    parser = argparse.ArgumentParser(description="Text-to-Speech using edge-tts")
    parser.add_argument("text", nargs="?", help="Text to speak")
    parser.add_argument("--voice", "-v", default="andrew",
                       help="Voice to use (default: andrew)")
    parser.add_argument("--output", "-o", help="Output file path (plays audio if not specified)")
    parser.add_argument("--rate", "-r", choices=["slow", "normal", "fast"], default="normal",
                       help="Speech rate (default: normal)")
    parser.add_argument("--list-voices", "-l", action="store_true",
                       help="List available voice shortcuts")

    args = parser.parse_args()

    if args.list_voices:
        print("Available voices:")
        for name, voice_id in VOICE_SHORTCUTS.items():
            default = " (default)" if name == "andrew" else ""
            print(f"  {name:10} -> {voice_id}{default}")
        return

    if not args.text:
        parser.error("text is required (unless using --list-voices)")

    voice = VOICE_SHORTCUTS.get(args.voice.lower(), args.voice)
    rate = RATE_MAP.get(args.rate, "+0%")

    save_to_file = args.output is not None
    output_path = args.output if save_to_file else tempfile.mktemp(suffix=".mp3")

    asyncio.run(generate_speech(args.text, voice, rate, output_path))

    if save_to_file:
        print(f"Audio saved to: {output_path}")
    else:
        play_audio(output_path)
        os.remove(output_path)


if __name__ == "__main__":
    main()
