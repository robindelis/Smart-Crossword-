import os
import sys
import json
import hashlib
import asyncio
import mimetypes
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

WEB_DIR = os.path.dirname(os.path.abspath(__file__))
MOBILE_DIR = os.path.abspath(os.path.join(WEB_DIR, "..", "mobile"))
CACHE_DIR = os.path.join(WEB_DIR, "audio_cache")
VOICE_NOTES_DIR = os.path.join(CACHE_DIR, "voice_notes")

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(VOICE_NOTES_DIR, exist_ok=True)

# Ensure MIME types include WebAssembly and modern formats
mimetypes.add_type("application/wasm", ".wasm")
mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("audio/webm", ".webm")
mimetypes.add_type("application/javascript", ".js")

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
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_HEAD(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/tts":
            self.send_response(200)
            self.send_header("Content-Type", "audio/mpeg")
            self.send_cors_headers()
            self.end_headers()
            return
        super().do_HEAD()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. Neural TTS API
        if path == "/api/tts":
            params = urllib.parse.parse_qs(parsed.query)
            text = params.get("text", [""])[0]
            lang = params.get("lang", ["en"])[0]

            if not text:
                self.send_response(400)
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(b"Missing text parameter")
                return

            mp3_path = generate_tts_sync(text, lang)
            if not mp3_path or not os.path.exists(mp3_path):
                self.send_response(500)
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(b"TTS generation failed")
                return

            with open(mp3_path, "rb") as f:
                data = f.read()

            self.send_response(200)
            self.send_header("Content-Type", "audio/mpeg")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "public, max-age=86400")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(data)
            return

        # 2. Board Status API endpoint (e.g. /api/board/SCB-8492/status)
        if path.startswith("/api/board/") and path.endswith("/status"):
            parts = path.strip("/").split("/")
            board_id = parts[2].upper() if len(parts) >= 3 else "SCB-8492"
            status_data = {
                "board_id": board_id,
                "status": "online",
                "connected": True,
                "rfid_matrix": "15x15",
                "last_ping": int(urllib.parse.time.time()) if hasattr(urllib.parse, "time") else 0
            }
            body = json.dumps(status_data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(body)
            return

        # 3. Voice note playback endpoint (/api/voice-note/<id>)
        if path.startswith("/api/voice-note/"):
            note_id = os.path.basename(path)
            note_file = os.path.join(VOICE_NOTES_DIR, f"{note_id}.webm")
            if os.path.exists(note_file):
                with open(note_file, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "audio/webm")
                self.send_header("Content-Length", str(len(data)))
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(data)
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        # 4. Global dictionary files (/dict_*.txt) fallback
        if path.startswith("/dict_") and path.endswith(".txt"):
            dict_file = os.path.join(WEB_DIR, os.path.basename(path))
            if os.path.exists(dict_file):
                self.serve_static_file(dict_file, "text/plain; charset=utf-8")
                return

        # 5. Serve Mobile PWA app files (/mobile and /mobile/*)
        if path == "/mobile" or path == "/mobile/":
            index_path = os.path.join(MOBILE_DIR, "index.html")
            self.serve_static_file(index_path, "text/html; charset=utf-8")
            return

        if path.startswith("/mobile/"):
            rel_path = path[len("/mobile/"):]
            file_path = os.path.join(MOBILE_DIR, rel_path)

            if os.path.isdir(file_path):
                file_path = os.path.join(file_path, "index.html")

            if os.path.exists(file_path) and os.path.isfile(file_path):
                content_type, _ = mimetypes.guess_type(file_path)
                if not content_type:
                    if file_path.endswith(".wasm"):
                        content_type = "application/wasm"
                    elif file_path.endswith(".json"):
                        content_type = "application/json"
                    else:
                        content_type = "application/octet-stream"

                self.serve_static_file(file_path, content_type)
                return
            else:
                # PWA Navigation Fallback to index.html for client-side routing
                index_path = os.path.join(MOBILE_DIR, "index.html")
                if os.path.exists(index_path) and not "." in os.path.basename(path):
                    self.serve_static_file(index_path, "text/html; charset=utf-8")
                    return
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"File not found in /mobile")
                return

        # Default: serve web directory files
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. Voice Note upload endpoint (/api/voice-note)
        if path == "/api/voice-note":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)

            note_id = f"vn_{hashlib.md5(post_data).hexdigest()[:10]}"
            note_file = os.path.join(VOICE_NOTES_DIR, f"{note_id}.webm")

            with open(note_file, "wb") as f:
                f.write(post_data)

            response = {
                "ok": True,
                "id": note_id,
                "url": f"/api/voice-note/{note_id}"
            }
            body = json.dumps(response).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(body)
            return

        # 2. Board Move sync endpoint (/api/board/<board_id>/move)
        if path.startswith("/api/board/") and path.endswith("/move"):
            parts = path.strip("/").split("/")
            board_id = parts[2].upper() if len(parts) >= 3 else "SCB-8492"

            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)

            response = {
                "ok": True,
                "board_id": board_id,
                "synced": True
            }
            body = json.dumps(response).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.end_headers()

    def serve_static_file(self, file_path, content_type):
        try:
            with open(file_path, "rb") as f:
                data = f.read()

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            if content_type.startswith("image/") or content_type == "application/wasm":
                self.send_header("Cache-Control", "public, max-age=86400")
            else:
                self.send_header("Cache-Control", "no-cache")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(500)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(f"Error reading file: {e}".encode("utf-8"))

def run(port=8080):
    server = HTTPServer(("0.0.0.0", port), GameRequestHandler)
    print(f"Smart Crossword Server running on http://0.0.0.0:{port}")
    print(f"Web interface:    http://0.0.0.0:{port}/")
    print(f"Mobile companion: http://0.0.0.0:{port}/mobile/")
    server.serve_forever()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run(port)
