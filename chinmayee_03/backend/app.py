from flask import send_from_directory
from flask import Flask, request, jsonify
from flask_cors import CORS
import secrets
import string
import re

app = Flask(__name__)
CORS(app, resources={r'/api/*': {'origins': '*'}})

CHARSETS = {
    "uppercase": string.ascii_uppercase,
    "lowercase": string.ascii_lowercase,
    "numbers": string.digits,
    "symbols": "!@#$%^&*()_+-=[]{}|;:,.<>?/"
}
AMBIGUOUS = set("0Ol1")

WORDS = [
    "river","mountain","forest","ocean","planet","silver","rocket","tiger",
    "coffee","garden","cloud","thunder","sunset","orange","crystal","falcon",
    "winter","summer","violet","shadow","bridge","castle","panda","diamond",
    "moon","star","eagle","cactus","laptop","meadow","comet","island",
    "lantern","breeze","signal","willow","marble","ember","harbor","aurora"
]

def clean_charset(chars, exclude_ambiguous=False, exclude_chars=""):
    blocked = set(exclude_chars or "")
    if exclude_ambiguous:
        blocked |= AMBIGUOUS
    return "".join(c for c in chars if c not in blocked)

def strength(password):
    score = 0
    if len(password) >= 8: score += 1
    if len(password) >= 12: score += 1
    if len(password) >= 16: score += 1
    if len(password) >= 24: score += 1
    if re.search(r"[A-Z]", password): score += 1
    if re.search(r"[a-z]", password): score += 1
    if re.search(r"[0-9]", password): score += 1
    if re.search(r"[^A-Za-z0-9]", password): score += 1
    label = "Weak" if score <= 3 else "Medium" if score <= 6 else "Strong"
    return {"score": score, "label": label}

def generate_secure_password(length, types, exclude_ambiguous=False,
                             no_repeat=False, exclude_chars=""):
    if not isinstance(length, int) or length < 8 or length > 128:
        raise ValueError("Password length must be between 8 and 128.")
    if not isinstance(types, list) or len(types) < 2:
        raise ValueError("Select at least 2 character types.")
    if any(t not in CHARSETS for t in types):
        raise ValueError("Invalid character type.")

    pools = {}
    for t in types:
        pool = clean_charset(CHARSETS[t], exclude_ambiguous, exclude_chars)
        if not pool:
            raise ValueError(f"No available characters remain for {t}.")
        pools[t] = pool

    combined = "".join(pools.values())
    if no_repeat and len(set(combined)) < length:
        raise ValueError("No-repeat mode cannot satisfy this length with the selected rules.")

    password = [secrets.choice(pools[t]) for t in types]

    while len(password) < length:
        c = secrets.choice(combined)
        if no_repeat and c in password:
            continue
        password.append(c)

    secrets.SystemRandom().shuffle(password)
    return "".join(password)

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "SecurePass backend"})

@app.post("/api/generate")
def generate():
    data = request.get_json(silent=True) or {}
    try:
        password = generate_secure_password(
            int(data.get("length", 20)),
            data.get("types", []),
            bool(data.get("exclude_ambiguous", False)),
            bool(data.get("no_repeat", False)),
            str(data.get("exclude_chars", ""))
        )
        return jsonify({"password": password, "strength": strength(password)})
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400

@app.post("/api/passphrase")
def passphrase():
    data = request.get_json(silent=True) or {}
    try:
        count = int(data.get("words", 5))
        if not 3 <= count <= 10:
            raise ValueError("Number of words must be between 3 and 10.")
        separator = str(data.get("separator", "-"))
        if separator not in {"-", "_", ".", " "}:
            raise ValueError("Invalid separator.")
        selected = [secrets.choice(WORDS) for _ in range(count)]
        phrase = separator.join(selected)
        return jsonify({"passphrase": phrase})
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400

# Serve the frontend directly from Flask so the app works without opening index.html
# via file:// (which commonly causes browser "Failed to fetch" errors).
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

@app.get("/")
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.get("/<path:filename>")
def serve_frontend_assets(filename):
    # Never shadow API routes.
    if filename.startswith("api/"):
        return {"error": "Not found"}, 404
    return send_from_directory(FRONTEND_DIR, filename)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
