"""General-purpose AI engine for Nova Voice Assistant.

Every message that is not an explicit local computer action is sent here. OpenAI
is the primary provider and can use web search for current information. Gemini is
supported as a second provider. Free web sources are only an emergency fallback.
"""
import html
import re
import urllib.parse
from html.parser import HTMLParser
from typing import List

import requests
import config

logger = config.logger

SYSTEM_PROMPT = f"""You are {config.ASSISTANT_NAME}, a capable general-purpose AI assistant.

Answer the user's actual question directly. You are not limited to dashboard commands.
Handle general knowledge, science, mathematics, programming, computer science,
education, writing, translation, explanations, comparisons, reasoning, planning,
brainstorming, and everyday questions.

For current, recent, changing, or location-specific facts, use web search when available.
Do not invent facts, dates, prices, events, citations, or people. If something is uncertain,
say so briefly. Use conversation history for follow-up questions.

The answer may be spoken aloud, so be natural and clear. Avoid unnecessary headings,
markdown tables, decorative symbols, and filler. When the user asks for code, provide the
code and a short explanation.
"""


def clean_tts(text: str) -> str:
    text = re.sub(r"```.*?```", "", text or "", flags=re.S)
    text = re.sub(r"[*_#]+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


class _SearchResultParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.in_snippet = False
        self.title = ""
        self.snippet = ""
        self.results = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "")
        if tag == "a" and "result__a" in classes:
            self.in_title = True
            self.title = ""
        elif "result__snippet" in classes:
            self.in_snippet = True
            self.snippet = ""

    def handle_endtag(self, tag):
        if tag == "a" and self.in_title:
            self.in_title = False
        if self.in_snippet and tag in ("a", "div"):
            self.in_snippet = False
            if self.title.strip() and self.snippet.strip():
                self.results.append((self.title.strip(), self.snippet.strip()))

    def handle_data(self, data):
        data = " ".join(data.split())
        if self.in_title:
            self.title += " " + data
        elif self.in_snippet:
            self.snippet += " " + data


class LLMEngine:
    def __init__(self):
        self.enabled = config.USE_LLM_FALLBACK
        self.openai_key = config.OPENAI_API_KEY.strip()
        self.openai_model = config.OPENAI_MODEL.strip() or "gpt-5.6-luna"
        self.gemini_key = config.GEMINI_API_KEY.strip()
        self.gemini_model = config.GEMINI_MODEL.strip() or "gemini-3.7-flash"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "NovaVoiceAssistant/5.0"})
        self.history = []
        self.max_history = 20
        self.last_error = ""

    @property
    def provider(self):
        if not self.enabled:
            return "disabled"
        if self.openai_key:
            return "openai"
        if self.gemini_key:
            return "gemini"
        return "web-fallback"

    def status(self):
        return {
            "enabled": self.enabled,
            "provider": self.provider,
            "openai_configured": bool(self.openai_key),
            "gemini_configured": bool(self.gemini_key),
            "model": self.openai_model if self.openai_key else (self.gemini_model if self.gemini_key else None),
            "ready_for_general_ai": bool(self.enabled and (self.openai_key or self.gemini_key)),
            "last_error": self.last_error[-500:] if self.last_error else "",
        }

    def generate_response(self, user_text: str) -> str:
        text = re.sub(r"\s+", " ", (user_text or "").strip())
        if not text:
            return "Please ask me a question or give me a command."

        local = self._local_conversation(text)
        if local:
            self._remember(text, local)
            return local

        self.last_error = ""

        if self.enabled and self.openai_key:
            # Try live web search first, then normal AI, so a web-tool mismatch or
            # temporary search failure never prevents ordinary AI answers.
            for use_web in (True, False):
                try:
                    answer = self.query_openai(text, use_web=use_web)
                    if answer:
                        return answer
                except Exception as exc:
                    self.last_error = str(exc)
                    logger.warning("OpenAI request failed (web=%s): %s", use_web, exc)

        if self.enabled and self.gemini_key:
            try:
                answer = self.query_gemini(text)
                if answer:
                    return answer
            except Exception as exc:
                self.last_error = str(exc)
                logger.warning("Gemini request failed: %s", exc)

        # Emergency knowledge-only fallback. This is intentionally never presented
        # as equivalent to the AI model.
        for lookup in (self._query_duckduckgo_instant, self._query_wikipedia, self._query_duckduckgo_search):
            try:
                answer = lookup(text)
                if answer:
                    self._remember(text, answer)
                    return answer
            except Exception as exc:
                logger.debug("Knowledge lookup failed: %s", exc)

        if not self.enabled or (not self.openai_key and not self.gemini_key):
            return ("General AI is not configured yet. Add an OpenAI or Gemini API key to the .env file, "
                    "restart the server, and then I can answer general questions.")
        return "I could not get a reliable AI response right now. Please try again."

    def _remember(self, user, assistant):
        self.history.append({"role": "user", "content": user})
        self.history.append({"role": "assistant", "content": assistant})
        self.history = self.history[-self.max_history:]

    def query_openai(self, prompt: str, use_web: bool = True) -> str:
        url = "https://api.openai.com/v1/responses"
        headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}
        messages = [{"role": "developer", "content": SYSTEM_PROMPT}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": prompt})
        payload = {"model": self.openai_model, "input": messages, "max_output_tokens": 1600}

        if use_web:
            # Current Responses API tool name. If an account/API version rejects it,
            # generate_response immediately retries without web search.
            payload["tools"] = [{"type": "web_search"}]
            payload["tool_choice"] = "auto"

        response = self.session.post(url, headers=headers, json=payload, timeout=90)
        if response.status_code != 200:
            raise RuntimeError(f"OpenAI HTTP {response.status_code}: {response.text[:900]}")

        data = response.json()
        answer = (data.get("output_text") or "").strip()
        if not answer:
            parts = []
            for item in data.get("output", []) or []:
                if isinstance(item, dict):
                    for content in item.get("content", []) or []:
                        if isinstance(content, dict) and content.get("type") == "output_text":
                            parts.append(content.get("text", ""))
            answer = " ".join(parts).strip()
        answer = clean_tts(answer)
        if not answer:
            raise RuntimeError("OpenAI returned no text output")
        self._remember(prompt, answer)
        return answer

    def query_gemini(self, prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent"
        contents = []
        for item in self.history:
            role = "model" if item["role"] == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": item["content"]}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})
        payload = {
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": contents,
            "generationConfig": {"maxOutputTokens": 1600, "temperature": 0.2},
        }
        response = self.session.post(
            url,
            headers={"x-goog-api-key": self.gemini_key, "Content-Type": "application/json"},
            json=payload,
            timeout=90,
        )
        if response.status_code != 200:
            raise RuntimeError(f"Gemini HTTP {response.status_code}: {response.text[:900]}")
        data = response.json()
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        answer = clean_tts(" ".join(p.get("text", "") for p in parts if p.get("text")))
        if not answer:
            raise RuntimeError("Gemini returned no text output")
        self._remember(prompt, answer)
        return answer

    def _local_conversation(self, text):
        low = text.lower()
        if re.match(r"^(hi|hello|hey|good morning|good afternoon|good evening)\b", low):
            return f"Hello {config.USER_NAME}! What would you like to know?"
        if re.search(r"\bhow are you\b", low):
            return "I am doing well and ready to help. Ask me anything."
        if re.search(r"\b(who are you|what is your name)\b", low):
            return f"I am {config.ASSISTANT_NAME}, your AI voice assistant. I can answer general questions and perform supported computer commands."
        if re.search(r"\b(thank you|thanks)\b", low):
            return "You're welcome!"
        return ""

    def _question_query(self, text):
        q = re.sub(r"[?!.]+$", "", text).strip()
        q = re.sub(r"^(please\s+)?(can you|could you|would you|tell me|explain|define)\s+", "", q, flags=re.I)
        return q.strip()

    def _query_duckduckgo_instant(self, text):
        query = self._question_query(text)
        if len(query) < 2:
            return ""
        response = self.session.get("https://api.duckduckgo.com/", params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 0}, timeout=8)
        if response.status_code != 200:
            return ""
        data = response.json()
        answer = data.get("Answer", "").strip() or data.get("AbstractText", "").strip()
        if answer:
            return clean_tts(html.unescape(self._first_sentences(answer, 4)))
        for item in data.get("RelatedTopics", []):
            if isinstance(item, dict) and item.get("Text"):
                return clean_tts(item["Text"])
        return ""

    def _query_wikipedia(self, text):
        query = self._question_query(text)
        if len(query) < 2:
            return ""
        search = self.session.get("https://en.wikipedia.org/w/api.php", params={"action": "opensearch", "search": query, "limit": 3, "namespace": 0, "format": "json"}, headers={"User-Agent": "NovaVoiceAssistant/5.0"}, timeout=8)
        if search.status_code != 200:
            return ""
        data = search.json()
        titles: List[str] = data[1] if len(data) > 1 else []
        for title in titles:
            page = self.session.get("https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(title.replace(" ", "_")), headers={"User-Agent": "NovaVoiceAssistant/5.0"}, timeout=8)
            if page.status_code == 200:
                extract = page.json().get("extract", "").strip()
                if extract:
                    return clean_tts(self._first_sentences(extract, 4))
        return ""

    def _query_duckduckgo_search(self, text):
        response = self.session.get("https://html.duckduckgo.com/html/", params={"q": text}, timeout=10)
        if response.status_code != 200:
            return ""
        parser = _SearchResultParser()
        parser.feed(response.text)
        if not parser.results:
            return ""
        return clean_tts(" ".join(f"{title}: {snippet}" for title, snippet in parser.results[:3]))

    @staticmethod
    def _first_sentences(text, count=4):
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return " ".join(s for s in sentences[:count] if s)
