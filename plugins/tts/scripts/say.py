#!/usr/bin/env python3
"""Minimal TTS with auto-chunking for low latency and seamless playback."""
import sys, asyncio, tempfile, time, os, re, threading, queue

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

CHUNK_WORDS = 8

def get_text():
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:])
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    return None

def sanitize(text):
    text = text.replace("\\n", ". ").replace("\n", ". ")
    text = text.replace("\\r", " ").replace("\r", " ")
    text = text.replace("_", " ")
    return text

def split_into_chunks(text):
    """Split text at sentence boundaries."""
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

async def generate(text, path):
    import edge_tts
    await edge_tts.Communicate(text, "en-US-AndrewNeural").save(path)

def generate_and_load(text, pygame, result_queue):
    """Generate audio and preload Sound object."""
    tmp = tempfile.mktemp(suffix=".mp3")
    try:
        asyncio.run(generate(text, tmp))
        sound = pygame.mixer.Sound(tmp)
        result_queue.put(("ok", sound, tmp))
    except Exception as e:
        result_queue.put(("error", None, str(e)))

def speak_chunked(text):
    import pygame

    chunks = split_into_chunks(text)
    files_to_cleanup = []

    pygame.mixer.init(frequency=24000)

    try:
        if len(chunks) == 1:
            tmp = tempfile.mktemp(suffix=".mp3")
            files_to_cleanup.append(tmp)
            asyncio.run(generate(chunks[0], tmp))
            sound = pygame.mixer.Sound(tmp)
            sound.play()
            while pygame.mixer.get_busy():
                time.sleep(0.01)
            return

        current_q = queue.Queue()
        current_t = threading.Thread(target=generate_and_load, args=(chunks[0], pygame, current_q))
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
                next_t = threading.Thread(target=generate_and_load, args=(chunks[i + 1], pygame, next_q))
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
    text = get_text()
    if not text:
        print("Usage: say \"text\" or echo \"text\" | say")
        sys.exit(1)
    try:
        speak_chunked(sanitize(text))
    except Exception as e:
        print(f"TTS error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
