import os
import sys
import hashlib
import asyncio
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

CACHE_DIR = os.path.join(os.path.dirname(__file__), "audio_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

VOICES = {
    "en": "en-US-JennyNeural",
    "fr": "fr-FR-DeniseNeural",
    "nl": "nl-NL-FennaNeural",
    "de": "de-DE-KatjaNeural",
    "es": "es-ES-ElviraNeural"
}

def generate_tts_sync(text, lang):
    voice = VOICES.get(lang, "en-US-JennyNeural")
    cache_key = hashlib.md5(f"{lang}:{voice}:{text}".encode("utf-8")).hexdigest()
    file_path = os.path.join(CACHE_DIR, f"{cache_key}.mp3")

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    try:
        import edge_tts
        async def _gen():
            comm = edge_tts.Communicate(text, voice, rate="-5%")
            await comm.save(file_path)
        asyncio.run(_gen())
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path
    except Exception as e:
        print(f"edge-tts error: {e}", file=sys.stderr)

    # Fallback to gTTS if edge-tts fails
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang=lang)
        tts.save(file_path)
        return file_path
    except Exception as e:
        print(f"gTTS error: {e}", file=sys.stderr)
        return None

class GameRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(__file__), **kwargs)

    def do_HEAD(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/tts":
            self.send_response(200)
            self.send_header("Content-Type", "audio/mpeg")
            self.end_headers()
            return
        super().do_HEAD()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/tts":
            params = urllib.parse.parse_qs(parsed.query)
            text = params.get("text", [""])[0]
            lang = params.get("lang", ["en"])[0]

            if not text:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing text parameter")
                return

            mp3_path = generate_tts_sync(text, lang)
            if not mp3_path or not os.path.exists(mp3_path):
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"TTS generation failed")
                return

            with open(mp3_path, "rb") as f:
                data = f.read()

            self.send_response(200)
            self.send_header("Content-Type", "audio/mpeg")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "public, max-age=86400")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data)
            return

        super().do_GET()

def run(port=8080):
    server = HTTPServer(("0.0.0.0", port), GameRequestHandler)
    print(f"Smart Crossword Server running on http://0.0.0.0:{port} with Neural TTS enabled")
    server.serve_forever()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run(port)
