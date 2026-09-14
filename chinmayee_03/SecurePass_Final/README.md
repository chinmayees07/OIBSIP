# VaultKey — Secure Password Studio

A polished full-stack password security dashboard with a Python Flask backend and a responsive HTML/CSS/JavaScript frontend.

## Important: fix for "Failed to fetch"

Do **not** open `frontend/index.html` directly by double-clicking it.

Start the Flask server first:

### Windows
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open:

**http://127.0.0.1:5000**

The Flask server now serves both the API and the frontend, which avoids browser CORS/file-origin problems that cause `Failed to fetch`.

## Features

- Professional SaaS-style security dashboard
- Password generation with secure Python `secrets`
- Guaranteed selected character categories
- Ambiguous-character exclusion
- Custom exclusions
- No-repeat option
- Strength indicator
- Browser-local password analyzer
- Secure passphrase generator
- Copy to clipboard
- Last 5 credentials in session memory only
- Dark mode
- Compact interface mode
- Automatic-copy preference
- Backend health indicator
- Local browser fallback if the Python API is temporarily unavailable

## API

- `GET /api/health`
- `POST /api/generate`
- `POST /api/passphrase`

## Security note

Generated credentials are not persisted by the application. Session history exists only in browser memory and is cleared when the page/session is closed.
