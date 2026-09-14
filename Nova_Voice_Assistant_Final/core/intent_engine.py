"""
Intent Processing Engine
Dispatches transcribed voice commands to modular action handlers.
Supports pattern matching, regex extraction, priority ordering, and optional LLM fallback.
"""

import re
from typing import Callable, List, Dict, Any, Optional
import config

logger = config.logger


class Intent:
    """Represents a discrete voice command capability."""
    def __init__(
        self,
        name: str,
        handler: Callable[[str, Dict[str, Any]], str],
        patterns: List[str] = None,
        regex_patterns: List[str] = None,
        description: str = "",
        requires_internet: bool = False
    ):
        self.name = name
        self.handler = handler
        self.patterns = [p.lower() for p in (patterns or [])]
        self.regex_patterns = [re.compile(r, re.IGNORECASE) for r in (regex_patterns or [])]
        self.description = description
        self.requires_internet = requires_internet

    def match(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Tests if the input text matches this intent.
        Returns extracted parameters dict if matched, otherwise None.
        """
        text_clean = text.strip().lower()

        # 1. Exact or keyword phrase matching
        for pattern in self.patterns:
            if pattern in text_clean:
                # Extract any remaining arguments after the trigger pattern
                args = text_clean.replace(pattern, "").strip()
                return {"matched_pattern": pattern, "args": args}

        # 2. Regular Expression matching with named groups
        for regex in self.regex_patterns:
            match = regex.search(text_clean)
            if match:
                extracted = match.groupdict()
                extracted["matched_pattern"] = regex.pattern
                return extracted

        return None


class IntentEngine:
    """Registry and dispatcher for all voice assistant intents."""
    def __init__(self, fallback_handler: Optional[Callable[[str], str]] = None):
        self._intents: List[Intent] = []
        self.fallback_handler = fallback_handler

    def register_intent(
        self,
        name: str,
        patterns: List[str] = None,
        regex_patterns: List[str] = None,
        description: str = "",
        requires_internet: bool = False
    ):
        """Decorator to register a function as an intent handler."""
        def decorator(handler_func: Callable[[str, Dict[str, Any]], str]):
            intent = Intent(
                name=name,
                handler=handler_func,
                patterns=patterns,
                regex_patterns=regex_patterns,
                description=description,
                requires_internet=requires_internet
            )
            self._intents.append(intent)
            logger.debug(f"Registered intent: '{name}' with {len(patterns or []) + len(regex_patterns or [])} trigger patterns.")
            return handler_func
        return decorator

    def process(self, text: str) -> str:
        """
        Processes transcribed user speech and returns the assistant's response string.
        """
        if not text or not text.strip():
            return ""

        text_clean = text.strip().lower()
        logger.info(f"Processing intent for command: \"{text_clean}\"")

        # Iterate through registered intents in order
        for intent in self._intents:
            params = intent.match(text_clean)
            if params is not None:
                logger.info(f"Matched intent: '{intent.name}'")
                try:
                    response = intent.handler(text_clean, params)
                    return response
                except Exception as e:
                    logger.error(f"Error executing intent '{intent.name}': {e}", exc_info=True)
                    return f"Sorry, I encountered an error while trying to {intent.name.replace('_', ' ')}."

        # If no explicit rule matched, invoke fallback (conversational or LLM)
        if self.fallback_handler:
            logger.info("No rule matched. Routing to fallback handler...")
            return self.fallback_handler(text_clean)

        return "I'm sorry, I don't know how to handle that command yet. Try asking for the time, a web search, or to open an app."

    def list_commands(self) -> List[Dict[str, Any]]:
        """Returns metadata of all registered commands for documentation or UI help dialogs."""
        return [
            {
                "name": intent.name,
                "description": intent.description,
                "examples": intent.patterns[:2],
                "requires_internet": intent.requires_internet
            }
            for intent in self._intents
        ]
