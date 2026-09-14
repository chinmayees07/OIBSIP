"""
Web & Online Action Handlers
Handles opening websites, performing Google/YouTube searches, Wikipedia lookups, and weather reports.
"""

import urllib.parse
import webbrowser
import re
import requests
import wikipedia
import config

logger = config.logger


def open_website(text: str, params: dict) -> str:
    """Opens a predefined website or extracts domain from command."""
    text_clean = text.lower().strip()
    
    # 1. Match known website names in dictionary
    for site_key, site_url in config.WEBSITES.items():
        # Match word boundaries or phrases
        if re.search(r'\b' + re.escape(site_key) + r'\b', text_clean):
            webbrowser.open(site_url)
            return f"Opening {site_key.capitalize()} in your default browser."

    # 2. Extract potential domain e.g. "open amazon.com", "open cnn.com"
    cleaned_query = re.sub(r'^(open website|open site|open|go to|launch)\s+', '', text_clean).strip()
    if cleaned_query:
        if '.' in cleaned_query and not cleaned_query.startswith("http"):
            target_url = f"https://{cleaned_query}"
        elif not cleaned_query.startswith("http"):
            target_url = f"https://www.{cleaned_query}.com"
        else:
            target_url = cleaned_query
        webbrowser.open(target_url)
        return f"Opening {cleaned_query}."

    return "Which website would you like me to open?"


def search_google(text: str, params: dict) -> str:
    """Searches Google for the extracted query string."""
    query = text
    for prefix in ["search google for", "search the web for", "google search for", "search about", "search for", "google search", "google", "search", "find information about", "find"]:
        if prefix in query.lower():
            pattern = re.compile(re.escape(prefix), re.IGNORECASE)
            query = pattern.split(query, 1)[1].strip()
            break

    query = re.sub(r"^[?!.,\s]+|[?!.,\s]+$", "", query).strip()
    if not query:
        return "What would you like me to search for on Google?"

    encoded = urllib.parse.quote_plus(query)
    search_url = f"https://www.google.com/search?q={encoded}"
    webbrowser.open(search_url)
    return f"Searching Google for {query}."


def search_youtube(text: str, params: dict) -> str:
    """Searches or plays video/music on YouTube."""
    query = text
    for prefix in ["play on youtube", "search youtube for", "youtube search for", "play video", "play song", "listen to", "play on yt", "youtube", "play"]:
        if prefix in query.lower():
            pattern = re.compile(re.escape(prefix), re.IGNORECASE)
            query = pattern.split(query, 1)[1].strip()
            break

    query = re.sub(r"^[?!.,\s]+|[?!.,\s]+$", "", query).strip()
    if not query:
        return "What video or song would you like me to play on YouTube?"

    encoded = urllib.parse.quote_plus(query)
    search_url = f"https://www.youtube.com/results?search_query={encoded}"
    webbrowser.open(search_url)
    return f"Playing {query} on YouTube."


def search_wikipedia(text: str, params: dict) -> str:
    """Fetches a concise summary from Wikipedia or DuckDuckGo."""
    query = text
    for prefix in ["who is", "who was", "what is", "what was", "what are", "tell me about", "tell me regarding", "wikipedia search for", "wikipedia", "explain to me", "explain", "define", "meaning of", "history of", "where is", "capital of", "how do", "how does"]:
        if prefix in query.lower():
            pattern = re.compile(re.escape(prefix), re.IGNORECASE)
            query = pattern.split(query, 1)[1].strip()
            break

    query = re.sub(r"^[?!.,\s]+|[?!.,\s]+$", "", query).strip()
    if not query:
        return "What topic would you like to look up?"

    # Check if query is actually a mathematical expression
    if re.search(r'\b(square root|sqrt|percent|%|plus|minus|multiplied|times|divided|\+|\*|\/)\b', query) or (re.search(r'\d', query) and any(op in query for op in ["+", "-", "*", "/", "x"])):
        from actions.productivity_actions import calculate_math
        return calculate_math(text, params)

    try:
        logger.info(f"Querying Wikipedia REST API for: '{query}'")
        headers = {"User-Agent": "NovaVoiceAssistant/2.0 (contact: user@project.local)"}

        # 1. Direct REST lookup
        endpoint = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query.replace(' ', '_'))}"
        res = requests.get(endpoint, headers=headers, timeout=4)
        if res.status_code == 200:
            extract = res.json().get("extract", "").strip()
            if extract:
                cleaned = re.sub(r"\([^)]*\)", "", extract)
                sentences = [s.strip() for s in cleaned.split(".") if s.strip()]
                return ". ".join(sentences[:2]) + "."

        # 2. OpenSearch for best matching article title
        search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(query)}&limit=3&namespace=0&format=json"
        search_res = requests.get(search_url, headers=headers, timeout=4)
        if search_res.status_code == 200:
            data = search_res.json()
            titles = data[1] if len(data) > 1 else []
            if titles:
                top_endpoint = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(titles[0].replace(' ', '_'))}"
                res_top = requests.get(top_endpoint, headers=headers, timeout=4)
                if res_top.status_code == 200:
                    extract = res_top.json().get("extract", "").strip()
                    if extract:
                        cleaned = re.sub(r"\([^)]*\)", "", extract)
                        sentences = [s.strip() for s in cleaned.split(".") if s.strip()]
                        return ". ".join(sentences[:2]) + "."

        # Fallback to Google search
        encoded = urllib.parse.quote_plus(query)
        webbrowser.open(f"https://www.google.com/search?q={encoded}")
        return f"I couldn't find a direct summary for '{query}', so I opened Google search results for you."
    except Exception as e:
        logger.error(f"Wikipedia lookup error: {e}")
        encoded = urllib.parse.quote_plus(query)
        webbrowser.open(f"https://www.google.com/search?q={encoded}")
        return f"I opened Google search for '{query}'."



def get_weather(text: str, params: dict) -> str:
    """Fetches real-time weather using the free wttr.in weather API."""
    location = ""
    text_lower = text.lower()
    if " in " in text_lower:
        location = text_lower.split(" in ", 1)[1].strip()
    elif " for " in text_lower:
        location = text_lower.split(" for ", 1)[1].strip()
    elif " at " in text_lower:
        location = text_lower.split(" at ", 1)[1].strip()

    # Clean punctuation
    location = re.sub(r"[?!.,]", "", location).strip()

    try:
        target_location = urllib.parse.quote(location) if location else ""
        url = f"https://wttr.in/{target_location}?format=%C+%t+%w&m"
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and response.text:
            weather_data = response.text.strip()
            place_str = f"in {location.capitalize()}" if location else "locally"
            return f"The current weather {place_str} is {weather_data}."
        return "I was unable to retrieve the weather report right now."
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return "Could not retrieve weather information due to a connection error."


def register_web_intents(intent_engine):
    """Registers all web & online intents."""
    # Build list of website triggers
    website_patterns = [f"open {site}" for site in config.WEBSITES.keys()]
    website_patterns.extend(["open website", "go to website", "launch website", "open site"])

    intent_engine.register_intent(
        name="open_website",
        patterns=website_patterns,
        description="Opens websites like YouTube, Google, Spotify, Netflix, Amazon, etc.",
        requires_internet=True
    )(open_website)

    intent_engine.register_intent(
        name="search_youtube",
        patterns=["play on youtube", "search youtube for", "youtube search", "play song", "play video", "listen to", "play music", "play"],
        description="Searches and plays media on YouTube.",
        requires_internet=True
    )(search_youtube)

    intent_engine.register_intent(
        name="search_google",
        patterns=["search google for", "search the web for", "google search", "search about", "search for", "find on google"],
        description="Searches Google for any topic.",
        requires_internet=True
    )(search_google)

    intent_engine.register_intent(
        name="wikipedia_lookup",
        patterns=["who is", "who was", "what is", "what was", "tell me about", "wikipedia", "explain", "define", "meaning of", "history of", "where is", "capital of"],
        description="Looks up concise summaries and knowledge definitions.",
        requires_internet=True
    )(search_wikipedia)

    intent_engine.register_intent(
        name="get_weather",
        patterns=["what's the weather", "current weather", "weather report", "weather in", "how is the weather", "temperature today", "forecast", "weather today", "weather"],
        description="Fetches current weather and temperature.",
        requires_internet=True
    )(get_weather)

