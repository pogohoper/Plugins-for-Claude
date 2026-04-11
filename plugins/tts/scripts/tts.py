#!/usr/bin/env python3
"""Text-to-speech using edge-tts with chunked playback for low latency."""
import sys, asyncio, tempfile, time, os, re, threading, queue, argparse

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

CHUNK_WORDS = 8

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


def sanitize(text):
    text = text.replace("\\n", ". ").replace("\n", ". ")
    text = text.replace("\\r", " ").replace("\r", " ")
    text = text.replace("_", " ")
    return text


def split_into_chunks(text):
    """Split text at sentence boundaries, grouping short sentences."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if len(sentences) <= 1:
        return [text]

    chunks = [sentences[0]]
    current = []
    current_words = 0

    for sentence in sentences[1:]:
        words = len(sentence.split())
        if current_words + words > CHUNK_WORDS and current:
            chunks.append(" ".join(current))
            current = [sentence]
            current_words = words
        else:
            current.append(sentence)
            current_words += words

    if current:
        chunks.append(" ".join(current))

    return chunks


async def generate(text, path, voice, rate):
    import edge_tts
    await edge_tts.Communicate(text, voice, rate=rate).save(path)


def generate_and_load(text, pygame, voice, rate, result_queue):
    """Generate audio and preload Sound object in a thread."""
    tmp = tempfile.mktemp(suffix=".mp3")
    try:
        asyncio.run(generate(text, tmp, voice, rate))
        sound = pygame.mixer.Sound(tmp)
        result_queue.put(("ok", sound, tmp))
    except Exception as e:
        result_queue.put(("error", None, str(e)))


def speak_chunked(text, voice, rate):
    import pygame

    chunks = split_into_chunks(text)
    files_to_cleanup = []

    pygame.mixer.init(frequency=24000)

    try:
        if len(chunks) == 1:
            tmp = tempfile.mktemp(suffix=".mp3")
            files_to_cleanup.append(tmp)
            asyncio.run(generate(chunks[0], tmp, voice, rate))
            sound = pygame.mixer.Sound(tmp)
            sound.play()
            while pygame.mixer.get_busy():
                time.sleep(0.01)
            return

        # Pipeline: generate next chunk while current one plays
        current_q = queue.Queue()
        current_t = threading.Thread(
            target=generate_and_load, args=(chunks[0], pygame, voice, rate, current_q)
        )
        current_t.start()

        next_q = None
        next_t = None

        for i in range(len(chunks)):
            if i == 0:
                current_t.join()
                status, sound, file_or_err = current_q.get()
            else:
                next_t.join()
                status, sound, file_or_err = next_q.get()

            if status == "error":
                print(f"TTS error: {file_or_err}")
                return

            files_to_cleanup.append(file_or_err)

            if i + 1 < len(chunks):
                next_q = queue.Queue()
                next_t = threading.Thread(
                    target=generate_and_load,
                    args=(chunks[i + 1], pygame, voice, rate, next_q),
                )
                next_t.start()

            channel = sound.play()
            while channel.get_busy():
                time.sleep(0.01)

    finally:
        time.sleep(0.1)
        pygame.mixer.quit()
        for f in files_to_cleanup:
            if os.path.exists(f):
                os.remove(f)


def main():
    parser = argparse.ArgumentParser(description="Text-to-Speech using edge-tts")
    parser.add_argument("text", nargs="*", help="Text to speak")
    parser.add_argument("--voice", "-v", default="andrew",
                        help="Voice: andrew, guy, aria, ava, jenny, brian (default: andrew)")
    parser.add_argument("--rate", "-r", choices=["slow", "normal", "fast"], default="normal",
                        help="Speech rate (default: normal)")
    parser.add_argument("--output", "-o",
                        help="Save to file instead of playing")
    parser.add_argument("--list-voices", "-l", action="store_true",
                        help="List available voices")

    args = parser.parse_args()

    if args.list_voices:
        print("Available voices:")
        for name, voice_id in VOICE_SHORTCUTS.items():
            default = " (default)" if name == "andrew" else ""
            print(f"  {name:10} -> {voice_id}{default}")
        return

    # Get text from args or stdin
    if args.text:
        text = " ".join(args.text)
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    else:
        parser.error("text is required (unless using --list-voices)")
        return

    voice = VOICE_SHORTCUTS.get(args.voice.lower(), args.voice)
    rate = RATE_MAP.get(args.rate, "+0%")

    if args.output:
        asyncio.run(generate(sanitize(text), args.output, voice, rate))
        print(f"Audio saved to: {args.output}")
    else:
        speak_chunked(sanitize(text), voice, rate)


if __name__ == "__main__":
    main()
