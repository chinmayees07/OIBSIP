"""
Main Application Entry Point for Nova Voice Assistant
Wires STT, Intent Processing, Action Handlers, TTS, LLM Brain, and GUI together.
"""

import os
import sys
import threading
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from core.tts_engine import TTSEngine
from core.stt_engine import STTEngine
from core.intent_engine import IntentEngine
from ai.llm_engine import LLMEngine
from ui.gui import VoiceAssistantGUI

# Import action modules
from actions.system_actions import register_system_intents
from actions.web_actions import register_web_intents
from actions.productivity_actions import register_productivity_intents
from actions.app_actions import register_app_intents

logger = config.logger


class VoiceAssistantApp:
    def __init__(self):
        logger.info(f"Initializing {config.ASSISTANT_NAME} Application...")

        # 1. Initialize Graphical Interface
        self.gui = VoiceAssistantGUI(
            on_command_callback=self.process_command,
            on_mic_request=self.listen_and_process
        )

        # 2. Initialize Text-to-Speech Engine
        self.tts = TTSEngine(
            on_start_callback=lambda text: self.gui.update_status("speaking"),
            on_end_callback=lambda text: self.gui.update_status("idle")
        )

        # 3. Initialize Speech-to-Text Engine
        self.stt = STTEngine(
            on_state_change=self.gui.update_status
        )

        # 4. Initialize AI / Fallback Brain
        self.llm = LLMEngine()

        # 5. Initialize Intent Processing Engine
        self.intent_engine = IntentEngine(
            fallback_handler=self.llm.generate_response
        )

        # 6. Register all modular intents
        self._register_all_intents()

        # 7. Pre-calibrate microphone in background
        threading.Thread(target=self._background_calibration, daemon=True).start()

    def _register_all_intents(self):
        """Registers all domain-specific action modules with the intent engine."""
        register_system_intents(self.intent_engine)
        register_productivity_intents(self.intent_engine)
        register_app_intents(self.intent_engine)
        register_web_intents(self.intent_engine)
        logger.info("All intent modules successfully registered.")

    def _background_calibration(self):
        """Calibrates microphone ambient noise levels upon launch."""
        calibrated = self.stt.calibrate_microphone(duration=1.0)
        if calibrated:
            self.gui.log_system_message("Microphone calibrated for ambient noise.")
        else:
            self.gui.log_system_message("Microphone calibration skipped or unavailable.")

    def listen_and_process(self):
        """Captures voice input, transcribes it, and dispatches the command."""
        logger.info("Triggered voice capture...")
        spoken_text = self.stt.listen()

        if not spoken_text:
            self.gui.update_status("idle")
            return

        if spoken_text == "ERROR_MIC_UNAVAILABLE":
            self.gui.log_system_message("Microphone not detected or permission denied.")
            self.tts.speak("I cannot access your microphone. Please check your audio settings.")
            return

        if spoken_text == "ERROR_NETWORK_UNAVAILABLE":
            self.gui.log_system_message("Internet connection required for Google Speech Recognition.")
            self.tts.speak("Network connection error. Speech recognition requires an active internet connection.")
            return

        # Display user voice transcript in GUI
        self.gui.log_user_message(spoken_text)

        # Process transcribed command
        self.process_command(spoken_text)

    def process_command(self, command_text: str):
        """Executes intent matching, logs response, and speaks result."""
        if not command_text:
            return

        self.gui.update_status("processing")
        response = self.intent_engine.process(command_text)

        # Log assistant response to UI
        self.gui.log_assistant_message(response)

        # Speak the response aloud via TTS
        self.tts.speak(response)

    def run(self):
        """Runs the desktop GUI application."""
        try:
            # Greet user upon startup
            greeting = f"Hello {config.USER_NAME}! {config.ASSISTANT_NAME} is ready."
            self.gui.log_assistant_message(greeting)
            self.tts.speak(greeting)

            # Start GUI loop
            self.gui.run()
        except KeyboardInterrupt:
            logger.info("Application stopped by user.")
        finally:
            self.tts.stop()


def main():
    app = VoiceAssistantApp()
    app.run()


if __name__ == "__main__":
    main()
