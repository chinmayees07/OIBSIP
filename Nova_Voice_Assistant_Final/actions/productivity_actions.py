"""
Productivity & Utility Action Handlers
Handles notes management, safe math calculations, jokes, quotes, facts, riddles, and conversions.
"""

import ast
import operator
import random
import datetime
import math
import re
import config

logger = config.logger

# Curated clean jokes list for offline humor
JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why do Java developers wear glasses? Because they don't C-sharp!",
    "There are 10 types of people in the world: those who understand binary, and those who don't.",
    "A SQL query walks into a bar, walks up to two tables and asks: Can I join you?",
    "Why was the JavaScript developer sad? Because they didn't Node how to Express themselves!",
    "What is an algorithm? A word used by programmers when they do not want to explain what they did.",
    "Why do computers love nature? Because they have millions of branches and leaves!",
    "How does a computer get drunk? It takes screenshots!"
]

# Curated quotes
QUOTES = [
    "The only way to do great work is to love what you do. — Steve Jobs",
    "It always seems impossible until it's done. — Nelson Mandela",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. — Winston Churchill",
    "Believe you can and you're halfway there. — Theodore Roosevelt",
    "The future belongs to those who believe in the beauty of their dreams. — Eleanor Roosevelt",
    "Do what you can, with what you have, where you are. — Theodore Roosevelt",
    "Act as if what you do makes a difference. It does. — William James"
]

# Curated facts
FACTS = [
    "Did you know? Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible!",
    "Did you know? Octopuses have three hearts and blue blood.",
    "Did you know? The first computer programmer in history was Ada Lovelace in 1843.",
    "Did you know? A day on Venus is longer than a year on Venus.",
    "Did you know? Sound travels about 4 times faster in water than in air.",
    "Did you know? Bananas are naturally slightly radioactive because they contain high levels of potassium-40.",
    "Did you know? The hashtag symbol is technically called an octothorpe."
]

# Curated riddles
RIDDLES = [
    "Riddle: What has keys but can't open locks? Answer: A piano or a keyboard!",
    "Riddle: What has to be broken before you can use it? Answer: An egg!",
    "Riddle: I’m tall when I’m young, and I’m short when I’m old. What am I? Answer: A candle!",
    "Riddle: What goes up but never comes down? Answer: Your age!",
    "Riddle: What has hands but cannot clap? Answer: A clock!"
]

# Safe math operators map
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval_math_ast(node):
    """Safely evaluates an AST math expression without using dangerous eval()."""
    if isinstance(node, ast.Constant):  # Python 3.8+ numeric literal
        return node.value
    elif isinstance(node, ast.BinOp):
        left = _eval_math_ast(node.left)
        right = _eval_math_ast(node.right)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported operator: {op_type}")
    elif isinstance(node, ast.UnaryOp):
        operand = _eval_math_ast(node.operand)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type}")
    else:
        raise TypeError(f"Unsupported AST node: {type(node)}")


def calculate_math(text: str, params: dict) -> str:
    """Parses and calculates math expressions from natural speech."""
    expr_text = text.lower()
    
    # Check for square root
    if "square root of" in expr_text or "sqrt of" in expr_text or "sqrt" in expr_text:
        nums = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", expr_text)
        if nums:
            val = float(nums[0])
            if val < 0:
                return "Square root of negative numbers is not a real number."
            res = math.sqrt(val)
            res_str = int(res) if res.is_integer() else round(res, 4)
            return f"The square root of {val} is {res_str}."

    # Check for percentage: e.g. "what is 20 percent of 150" or "20% of 150"
    pct_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:percent|%)\s+of\s+(\d+(?:\.\d+)?)", expr_text)
    if pct_match:
        pct = float(pct_match.group(1))
        base = float(pct_match.group(2))
        res = (pct / 100.0) * base
        res_str = int(res) if res.is_integer() else round(res, 4)
        return f"{pct} percent of {base} is {res_str}."

    for prefix in ["calculate", "compute", "solve", "what is", "how much is", "evaluate"]:
        if prefix in expr_text:
            expr_text = expr_text.split(prefix, 1)[1].strip()
            break

    # Replace spoken words with arithmetic symbols
    expr_text = (
        expr_text.replace("plus", "+")
                 .replace("add", "+")
                 .replace("minus", "-")
                 .replace("subtract", "-")
                 .replace("multiplied by", "*")
                 .replace("times", "*")
                 .replace("divided by", "/")
                 .replace("divide", "/")
                 .replace("over", "/")
                 .replace("to the power of", "**")
                 .replace("power", "**")
                 .replace("x", "*")
    )
    # Strip non-math characters
    cleaned = re.sub(r"[^0-9\+\-\*\/\(\)\.\s]", "", expr_text).strip()

    if not cleaned:
        return "Please specify a valid arithmetic calculation."

    try:
        parsed = ast.parse(cleaned, mode='eval')
        result = _eval_math_ast(parsed.body)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        elif isinstance(result, float):
            result = round(result, 4)
        return f"The result is {result}."
    except Exception as e:
        logger.error(f"Math calculation failed for '{cleaned}': {e}")
        return "I could not compute that mathematical expression."


def handle_unit_conversion(text: str, params: dict) -> str:
    """Handles basic length, weight, temperature, and currency conversions."""
    t = text.lower()
    
    # Temperature: Celsius to Fahrenheit
    c_to_f = re.search(r"(\d+(?:\.\d+)?)\s*(?:celsius|c)\s+(?:to|in)\s+(?:fahrenheit|f)", t)
    if c_to_f:
        c = float(c_to_f.group(1))
        f = (c * 9/5) + 32
        return f"{c} degrees Celsius is {round(f, 2)} degrees Fahrenheit."
        
    # Temperature: Fahrenheit to Celsius
    f_to_c = re.search(r"(\d+(?:\.\d+)?)\s*(?:fahrenheit|f)\s+(?:to|in)\s+(?:celsius|c)", t)
    if f_to_c:
        f = float(f_to_c.group(1))
        c = (f - 32) * 5/9
        return f"{f} degrees Fahrenheit is {round(c, 2)} degrees Celsius."

    # Distance: km to miles
    km_to_mi = re.search(r"(\d+(?:\.\d+)?)\s*(?:km|kilometers|kilometer)\s+(?:to|in)\s+(?:miles|mile|mi)", t)
    if km_to_mi:
        km = float(km_to_mi.group(1))
        mi = km * 0.621371
        return f"{km} kilometers is approximately {round(mi, 2)} miles."

    # Distance: miles to km
    mi_to_km = re.search(r"(\d+(?:\.\d+)?)\s*(?:miles|mile|mi)\s+(?:to|in)\s+(?:km|kilometers|kilometer)", t)
    if mi_to_km:
        mi = float(mi_to_km.group(1))
        km = mi * 1.60934
        return f"{mi} miles is approximately {round(km, 2)} kilometers."

    # Weight: kg to pounds
    kg_to_lb = re.search(r"(\d+(?:\.\d+)?)\s*(?:kg|kilograms|kilos)\s+(?:to|in)\s+(?:pounds|lbs|pound)", t)
    if kg_to_lb:
        kg = float(kg_to_lb.group(1))
        lb = kg * 2.20462
        return f"{kg} kilograms is approximately {round(lb, 2)} pounds."

    # Weight: pounds to kg
    lb_to_kg = re.search(r"(\d+(?:\.\d+)?)\s*(?:pounds|lbs|pound)\s+(?:to|in)\s+(?:kg|kilograms|kilos)", t)
    if lb_to_kg:
        lb = float(lb_to_kg.group(1))
        kg = lb / 2.20462
        return f"{lb} pounds is approximately {round(kg, 2)} kilograms."

    return "I can convert units like Celsius to Fahrenheit, kilometers to miles, and kilograms to pounds."


def add_note(text: str, params: dict) -> str:
    """Appends a new note with timestamp to notes.txt."""
    note_content = text
    for prefix in ["take a note", "write a note", "add note", "make a note", "note that", "save note", "note"]:
        if prefix in note_content.lower():
            pattern = re.compile(re.escape(prefix), re.IGNORECASE)
            note_content = pattern.split(note_content, 1)[1].strip()
            break

    if not note_content:
        return "What would you like me to write down in your notes?"

    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
        with open(config.NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {note_content.capitalize()}\n")
        return f"Note saved: \"{note_content}\"."
    except Exception as e:
        logger.error(f"Failed to write note: {e}")
        return "I was unable to save the note to the file."


def read_notes(text: str, params: dict) -> str:
    """Reads all saved notes from notes.txt."""
    if not config.NOTES_FILE.exists():
        return "You have no saved notes."

    try:
        with open(config.NOTES_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            return "Your notes file is currently empty."

        summary = f"You have {len(lines)} note{'s' if len(lines) > 1 else ''}. "
        recent = lines[-3:]
        summary += " Here are your latest entries: " + "; ".join(recent)
        return summary
    except Exception as e:
        logger.error(f"Failed to read notes: {e}")
        return "Unable to access the notes file."


def clear_notes(text: str, params: dict) -> str:
    """Clears all saved notes."""
    try:
        with open(config.NOTES_FILE, "w", encoding="utf-8") as f:
            f.write("")
        return "All notes have been cleared."
    except Exception as e:
        logger.error(f"Failed to clear notes: {e}")
        return "Error clearing notes."


def tell_joke(text: str, params: dict) -> str:
    """Returns a random humorous programming joke."""
    return random.choice(JOKES)


def tell_quote(text: str, params: dict) -> str:
    """Returns an inspirational quote."""
    return random.choice(QUOTES)


def tell_fact(text: str, params: dict) -> str:
    """Returns a fun science/general fact."""
    return random.choice(FACTS)


def tell_riddle(text: str, params: dict) -> str:
    """Returns a brain teaser riddle."""
    return random.choice(RIDDLES)


def coin_flip(text: str, params: dict) -> str:
    """Simulates flipping a coin."""
    outcome = random.choice(["Heads", "Tails"])
    return f"I flipped a coin and got: {outcome}!"


def roll_dice(text: str, params: dict) -> str:
    """Simulates rolling a standard 6-sided die."""
    outcome = random.randint(1, 6)
    return f"I rolled a die and got: {outcome}!"


def register_productivity_intents(intent_engine):
    """Registers all productivity intents."""
    intent_engine.register_intent(
        name="calculate_math",
        patterns=["calculate", "compute", "solve", "how much is", "plus", "minus", "multiplied by", "divided by", "square root", "sqrt", "percent of", "% of", "+", "*"],
        description="Performs safe mathematical calculations.",
        requires_internet=False
    )(calculate_math)

    intent_engine.register_intent(
        name="unit_conversion",
        patterns=["convert", "celsius to fahrenheit", "fahrenheit to celsius", "km to miles", "miles to km", "kg to pounds", "pounds to kg"],
        description="Converts temperature, distance, and weight units.",
        requires_internet=False
    )(handle_unit_conversion)

    intent_engine.register_intent(
        name="add_note",
        patterns=["take a note", "write a note", "add note", "make a note", "save note", "note down", "remember that"],
        description="Appends a timestamped note to data/notes.txt.",
        requires_internet=False
    )(add_note)

    intent_engine.register_intent(
        name="read_notes",
        patterns=["read my notes", "read notes", "show notes", "what are my notes", "my notes", "list notes", "check notes"],
        description="Reads the latest notes from data/notes.txt.",
        requires_internet=False
    )(read_notes)

    intent_engine.register_intent(
        name="clear_notes",
        patterns=["clear notes", "delete all notes", "erase notes", "clear my notes"],
        description="Empties the notes file.",
        requires_internet=False
    )(clear_notes)

    intent_engine.register_intent(
        name="tell_joke",
        patterns=["tell me a joke", "make me laugh", "tell a joke", "say a joke", "another joke", "crack a joke", "joke"],
        description="Tells a humorous programming joke.",
        requires_internet=False
    )(tell_joke)

    intent_engine.register_intent(
        name="tell_quote",
        patterns=["tell me a quote", "give me a quote", "give me some motivation", "give me motivation", "inspire me", "motivate me", "motivation", "inspiration", "inspire", "quote of the day", "wisdom", "quote"],
        description="Gives an inspirational quote.",
        requires_internet=False
    )(tell_quote)

    intent_engine.register_intent(
        name="tell_fact",
        patterns=["tell me a fact", "fun fact", "did you know", "random fact", "interesting fact", "give me a fact", "fact"],
        description="Shares an interesting trivia or science fact.",
        requires_internet=False
    )(tell_fact)

    intent_engine.register_intent(
        name="tell_riddle",
        patterns=["tell me a riddle", "give me a riddle", "puzzle", "riddle"],
        description="Poses a brain-teaser riddle with answer.",
        requires_internet=False
    )(tell_riddle)

    intent_engine.register_intent(
        name="flip_coin",
        patterns=["flip a coin", "heads or tails", "toss a coin", "coin flip", "flip coin"],
        description="Flips a virtual coin.",
        requires_internet=False
    )(coin_flip)

    intent_engine.register_intent(
        name="roll_dice",
        patterns=["roll a dice", "roll die", "roll a die", "roll dice", "dice roll"],
        description="Rolls a standard 6-sided die.",
        requires_internet=False
    )(roll_dice)

