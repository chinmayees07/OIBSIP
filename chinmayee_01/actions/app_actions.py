"""
Application Launch Action Handlers
Opens installed desktop applications on the operating system.
"""

import subprocess
import sys
import re
import config

logger = config.logger


def launch_application(text: str, params: dict) -> str:
    """Launches local desktop applications registered in config.APP_MAPPINGS."""
    text_clean = text.lower().strip()
    
    # Sort app mappings by length descending so longer multi-word phrases match first (e.g. "task manager" before "task")
    sorted_apps = sorted(config.APP_MAPPINGS.items(), key=lambda x: len(x[0]), reverse=True)
    for app_name, command in sorted_apps:
        if re.search(r'\b' + re.escape(app_name) + r'\b', text_clean):
            if not command:
                return f"Sorry, {app_name.capitalize()} is not supported on this operating system."
            try:
                logger.info(f"Launching application '{app_name}' via command: {command}")
                if sys.platform == "win32":
                    subprocess.Popen(command, shell=True)
                else:
                    subprocess.Popen(command.split())
                return f"Opening {app_name.capitalize()}."
            except Exception as e:
                logger.error(f"Failed to launch application '{app_name}': {e}")
                return f"I encountered an error trying to launch {app_name}."

    return "I couldn't find that desktop application. You can ask me to open Notepad, Calculator, Paint, Terminal, Settings, Chrome, or Task Manager."


def register_app_intents(intent_engine):
    """Registers application launch intents."""
    patterns = [f"open {app}" for app in config.APP_MAPPINGS.keys()]
    patterns.extend(["launch app", "open app", "start app", "open application"])

    intent_engine.register_intent(
        name="open_app",
        patterns=patterns,
        description="Launches common desktop applications.",
        requires_internet=False
    )(launch_application)

