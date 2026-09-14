"""
Configuration Module for Voice Assistant
Centralizes paths, audio parameters, application mappings, and API keys.
"""

import os
import sys
import logging
from pathlib import Path

# Ensure UTF-8 output encoding across Windows shells
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Load environment variables if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
NOTES_FILE = DATA_DIR / "notes.txt"

# Assistant Identity
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Nova")
USER_NAME = os.getenv("USER_NAME", "Boss")

# Speech-to-Text (STT) Settings
STT_ENERGY_THRESHOLD = 300  # Minimum audio energy to consider for recording
STT_DYNAMIC_ENERGY = True   # Automatically adjust for ambient noise
STT_PAUSE_THRESHOLD = 0.8   # Seconds of non-speaking audio before phrase is complete
STT_PHRASE_TIME_LIMIT = 8   # Max seconds of listening per command
STT_TIMEOUT = 5             # Max seconds to wait before speech starts

# Text-to-Speech (TTS) Settings
TTS_RATE = int(os.getenv("TTS_RATE", 175))       # Speed of speech (words per minute)
TTS_VOLUME = float(os.getenv("TTS_VOLUME", 1.0)) # Volume level (0.0 to 1.0)
VOICE_GENDER = os.getenv("VOICE_GENDER", "female").lower() # 'female' or 'male'

# Optional LLM Settings
USE_LLM_FALLBACK = os.getenv("USE_LLM_FALLBACK", "true").lower() in ("true", "1", "yes")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

# Common Application Launch Commands (Windows / Cross-platform fallback)
APP_MAPPINGS = {
    "notepad": "notepad.exe" if sys.platform == "win32" else "gedit",
    "calculator": "calc.exe" if sys.platform == "win32" else "gnome-calculator",
    "calc": "calc.exe" if sys.platform == "win32" else "gnome-calculator",
    "cmd": "cmd.exe" if sys.platform == "win32" else "bash",
    "command prompt": "cmd.exe" if sys.platform == "win32" else "bash",
    "terminal": "wt.exe" if sys.platform == "win32" else "bash",
    "powershell": "powershell.exe" if sys.platform == "win32" else "bash",
    "paint": "mspaint.exe" if sys.platform == "win32" else "gimp",
    "explorer": "explorer.exe" if sys.platform == "win32" else "xdg-open .",
    "file explorer": "explorer.exe" if sys.platform == "win32" else "xdg-open .",
    "files": "explorer.exe" if sys.platform == "win32" else "xdg-open .",
    "task manager": "taskmgr.exe" if sys.platform == "win32" else "top",
    "taskmgr": "taskmgr.exe" if sys.platform == "win32" else "top",
    "control panel": "control.exe" if sys.platform == "win32" else "",
    "settings": "start ms-settings:" if sys.platform == "win32" else "",
    "browser": "start chrome" if sys.platform == "win32" else "google-chrome",
    "chrome": "start chrome" if sys.platform == "win32" else "google-chrome",
    "edge": "start msedge" if sys.platform == "win32" else "",
    "code": "code" if sys.platform == "win32" else "code",
    "vs code": "code" if sys.platform == "win32" else "code",
    "vscode": "code" if sys.platform == "win32" else "code",
    "word": "start winword" if sys.platform == "win32" else "",
    "excel": "start excel" if sys.platform == "win32" else "",
    "powerpoint": "start powerpnt" if sys.platform == "win32" else "",
}

# Popular Websites Shortcuts
WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://www.github.com",
    "wikipedia": "https://www.wikipedia.org",
    "reddit": "https://www.reddit.com",
    "stackoverflow": "https://stackoverflow.com",
    "gmail": "https://mail.google.com",
    "chatgpt": "https://chat.openai.com",
    "netflix": "https://www.netflix.com",
    "spotify": "https://open.spotify.com",
    "amazon": "https://www.amazon.com",
    "twitter": "https://www.twitter.com",
    "x": "https://www.x.com",
    "instagram": "https://www.instagram.com",
    "linkedin": "https://www.linkedin.com",
    "facebook": "https://www.facebook.com",
    "twitch": "https://www.twitch.tv",
    "discord": "https://discord.com",
    "whatsapp": "https://web.whatsapp.com",
    "maps": "https://maps.google.com",
    "google maps": "https://maps.google.com",
    "outlook": "https://outlook.live.com",
    "yahoo": "https://www.yahoo.com",
    "canva": "https://www.canva.com",
    "pinterest": "https://www.pinterest.com",
    "tiktok": "https://www.tiktok.com",
    "notion": "https://www.notion.so",
    "figma": "https://www.figma.com",
    "medium": "https://www.medium.com",
    "quora": "https://www.quora.com",
    "bing": "https://www.bing.com",
}

# Logging Configuration
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("VoiceAssistant")
