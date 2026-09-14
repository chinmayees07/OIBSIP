"""
Text-to-Speech (TTS) Engine
Converts text into audible speech using pyttsx3 (offline, low latency).
Runs speech tasks in a background thread to prevent UI freezing.
"""

import threading
import queue
import pyttsx3
import config

logger = config.logger


class TTSEngine:
    def __init__(self, on_start_callback=None, on_end_callback=None):
        """
        Initialize the TTS engine with optional callbacks for UI state updates.
        """
        self.on_start_callback = on_start_callback
        self.on_end_callback = on_end_callback
        self._speech_queue = queue.Queue()
        self._is_running = True
        self._lock = threading.Lock()

        # Start the background worker thread for speech processing
        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self._worker_thread.start()

    def _init_engine(self):
        """Initializes a local pyttsx3 engine instance per worker."""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', config.TTS_RATE)
            engine.setProperty('volume', config.TTS_VOLUME)

            voices = engine.getProperty('voices')
            if voices:
                selected_voice = voices[0].id
                # Attempt to match configured gender
                for voice in voices:
                    name_lower = voice.name.lower()
                    if config.VOICE_GENDER == "female" and ("zira" in name_lower or "female" in name_lower or "samantha" in name_lower):
                        selected_voice = voice.id
                        break
                    elif config.VOICE_GENDER == "male" and ("david" in name_lower or "male" in name_lower):
                        selected_voice = voice.id
                        break
                engine.setProperty('voice', selected_voice)
            return engine
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3 engine: {e}")
            return None

    def _process_queue(self):
        """Worker loop that dequeues phrases and speaks them sequentially."""
        engine = self._init_engine()

        while self._is_running:
            try:
                text = self._speech_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if text is None:  # Shutdown signal
                break

            if not text.strip():
                self._speech_queue.task_done()
                continue

            try:
                if self.on_start_callback:
                    self.on_start_callback(text)

                logger.info(f"Speaking: \"{text}\"")

                # If engine failed earlier, try re-initializing
                if engine is None:
                    engine = self._init_engine()

                if engine:
                    engine.say(text)
                    engine.runAndWait()
                else:
                    logger.warning(f"[TTS Fallback Console]: {text}")

            except Exception as e:
                logger.error(f"Error during speech synthesis: {e}")
                # Reset engine on error
                try:
                    engine = self._init_engine()
                except Exception:
                    pass
            finally:
                if self.on_end_callback:
                    self.on_end_callback(text)
                self._speech_queue.task_done()

    def speak(self, text: str, block: bool = False):
        """
        Queue text to be spoken.
        :param text: The string message to say.
        :param block: If True, waits until speech completes before returning.
        """
        if not text:
            return
        self._speech_queue.put(text)
        if block:
            self._speech_queue.join()

    def stop(self):
        """Stops the TTS worker thread cleanly."""
        self._is_running = False
        self._speech_queue.put(None)
