"""
Nova Voice Assistant — Web Server & REST API Controller
Serves the web application at http://localhost:5000 and connects browser voice/text
commands directly to the Python Intent Engine and action modules.
Runs using Python standard library with zero external web server dependencies!
"""

import http.server
import socketserver
import json
import os
import sys
import webbrowser
import threading
import mimetypes
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load config and core modules
import config
from core.intent_engine import IntentEngine
from ai.llm_engine import LLMEngine

# Import action modules
from actions.system_actions import register_system_intents
from actions.web_actions import register_web_intents
from actions.productivity_actions import register_productivity_intents
from actions.app_actions import register_app_intents

logger = config.logger
PORT = 5000
WEB_DIR = Path(__file__).resolve().parent / "web"

# Initialize Intent Engine & AI Brain
llm = LLMEngine()
intent_engine = IntentEngine(fallback_handler=llm.generate_response)
register_system_intents(intent_engine)
register_productivity_intents(intent_engine)
register_app_intents(intent_engine)
register_web_intents(intent_engine)
logger.info("Intent engine initialized with all action modules for Web API.")


class AssistantRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_OPTIONS(self):
        """Handle CORS pre-flight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Handles web page routing and API queries."""
        if self.path == '/api/status':
            self._handle_get_status()
        elif self.path == '/api/health':
            self._send_json({"status": "ok", "server": "running"})
        elif self.path == '/api/ai-status':
            self._handle_get_ai_status()
        elif self.path == '/api/notes':
            self._handle_get_notes()
        else:
            # Default to serving static files from the web/ directory
            if self.path == '/':
                self.path = '/index.html'
            super().do_GET()

    def do_POST(self):
        """Handles command execution API."""
        if self.path == '/api/command':
            self._handle_post_command()
        else:
            self.send_error(404, "Endpoint not found")

    def do_DELETE(self):
        """Handles notes clearing API."""
        if self.path == '/api/notes':
            self._handle_delete_notes()
        else:
            self.send_error(404, "Endpoint not found")

    def _handle_post_command(self):
        """Processes voice/text command through Python Intent Engine."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            payload = json.loads(post_data.decode('utf-8'))
            command_text = payload.get('command', '').strip()

            if not command_text:
                self._send_json({"response": "Please provide a valid command."})
                return

            logger.info(f"[Web Command Received]: \"{command_text}\"")
            response_text = intent_engine.process(command_text)
            logger.info(f"[Assistant Response]: \"{response_text}\"")

            self._send_json({
                "status": "success",
                "command": command_text,
                "response": response_text
            })

        except Exception as e:
            logger.error(f"Error processing command payload: {e}")
            self._send_json({"status": "error", "response": "Internal server processing error."}, status=500)

    def _handle_get_status(self):
        """Returns live CPU, RAM, and system metrics."""
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            battery = psutil.sensors_battery()
            battery_pct = battery.percent if battery else None
        except Exception:
            cpu, ram, battery_pct = 15, 45, 100

        self._send_json({
            "status": "online",
            "cpu": cpu,
            "ram": ram,
            "battery": battery_pct,
            "assistant": config.ASSISTANT_NAME
        })

    def _handle_get_ai_status(self):
        """Returns the configured AI provider without exposing secret keys."""
        self._send_json(llm.status())

    def _handle_get_notes(self):
        """Returns list of saved notes from data/notes.txt."""
        notes = []
        if config.NOTES_FILE.exists():
            try:
                with open(config.NOTES_FILE, "r", encoding="utf-8") as f:
                    notes = [line.strip() for line in f if line.strip()]
            except Exception as e:
                logger.error(f"Error reading notes: {e}")

        self._send_json({"notes": notes})

    def _handle_delete_notes(self):
        """Clears data/notes.txt."""
        try:
            with open(config.NOTES_FILE, "w", encoding="utf-8") as f:
                f.write("")
            self._send_json({"status": "success", "message": "All notes cleared."})
        except Exception as e:
            self._send_json({"status": "error", "message": str(e)}, status=500)

    def _send_json(self, data, status=200):
        """Helper to send JSON response with CORS headers."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        """Custom HTTP log format."""
        logger.debug(f"[HTTP Server] {self.address_string()} - {format % args}")


def open_browser():
    """Opens browser automatically after short delay."""
    import time
    time.sleep(0.8)
    url = f"http://localhost:{PORT}"
    logger.info(f"Opening {url} in your default browser...")
    webbrowser.open(url)


def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", PORT), AssistantRequestHandler) as httpd:
        print("\n" + "=" * 60)
        print(f"  🎙️  Nova AI Voice Assistant is running as a Web Application!")
        print(f"  🌐  Website URL: http://localhost:{PORT}")
        print("=" * 60 + "\n")
        
        # Open browser in separate thread
        threading.Thread(target=open_browser, daemon=True).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()


if __name__ == "__main__":
    run_server()
