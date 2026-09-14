"""
Speech-to-Text (STT) Engine
Captures microphone audio and converts it into text using Google Speech Recognition API.
Includes automatic ambient noise calibration and graceful error handling.
"""

import speech_recognition as sr
import config

logger = config.logger


class STTEngine:
    def __init__(self, on_state_change=None):
        """
        Initialize the STT engine.
        :param on_state_change: Callback function(state: str) to report 'listening', 'processing', 'idle', etc.
        """
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = config.STT_ENERGY_THRESHOLD
        self.recognizer.dynamic_energy_threshold = config.STT_DYNAMIC_ENERGY
        self.recognizer.pause_threshold = config.STT_PAUSE_THRESHOLD
        self.on_state_change = on_state_change
        self._is_calibrated = False

    def calibrate_microphone(self, duration: float = 1.0) -> bool:
        """
        Adjusts for ambient background noise to improve recognition accuracy.
        """
        try:
            with sr.Microphone() as source:
                logger.info(f"Calibrating microphone for {duration}s ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                self._is_calibrated = True
                logger.info(f"Calibration complete. Energy threshold set to: {self.recognizer.energy_threshold}")
                return True
        except Exception as e:
            logger.error(f"Microphone calibration failed: {e}")
            return False

    def listen(self, timeout: int = config.STT_TIMEOUT, phrase_time_limit: int = config.STT_PHRASE_TIME_LIMIT) -> str:
        """
        Captures a single voice command from the microphone and converts it to text.
        Returns lowercase transcribed string, or empty string on failure/timeout.
        """
        if self.on_state_change:
            self.on_state_change("listening")

        audio_data = None
        try:
            with sr.Microphone() as source:
                if not self._is_calibrated:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
                    self._is_calibrated = True

                logger.info("Listening for voice input...")
                audio_data = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

        except sr.WaitTimeoutError:
            logger.debug("Listening timed out: No speech detected within window.")
            if self.on_state_change:
                self.on_state_change("idle")
            return ""
        except (sr.Microphone.MicrophoneError, OSError) as e:
            logger.error(f"Microphone hardware error: {e}")
            if self.on_state_change:
                self.on_state_change("error")
            return "ERROR_MIC_UNAVAILABLE"
        except Exception as e:
            logger.error(f"Unexpected audio capture error: {e}")
            if self.on_state_change:
                self.on_state_change("idle")
            return ""

        if audio_data is None:
            if self.on_state_change:
                self.on_state_change("idle")
            return ""

        if self.on_state_change:
            self.on_state_change("processing")

        try:
            logger.info("Recognizing speech via Google STT...")
            text = self.recognizer.recognize_google(audio_data)
            logger.info(f"Transcribed Text: \"{text}\"")
            if self.on_state_change:
                self.on_state_change("idle")
            return text.strip().lower()

        except sr.UnknownValueError:
            logger.info("Speech recognition could not understand audio.")
            if self.on_state_change:
                self.on_state_change("idle")
            return ""
        except sr.RequestError as e:
            logger.error(f"Speech Recognition service request error: {e}")
            if self.on_state_change:
                self.on_state_change("error")
            return "ERROR_NETWORK_UNAVAILABLE"
        except Exception as e:
            logger.error(f"Speech recognition processing error: {e}")
            if self.on_state_change:
                self.on_state_change("idle")
            return ""
