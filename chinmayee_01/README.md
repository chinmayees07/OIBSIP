# Nova AI Voice Assistant

A local Windows voice assistant with browser UI, speech input/output, computer actions, and a general-purpose AI brain.

## Start

1. Install Python 3.10+.
2. Run `setup_ai.bat` or copy `.env.example` to `.env` and add an AI API key.
3. Run `run_web.bat`.
4. Open `http://localhost:5000`.

## AI behavior

Normal questions are routed to the AI brain. Explicit computer commands such as opening a website or calculator remain local actions. Broad phrases such as `what is`, `who is`, `explain`, and `how does` are NOT treated as browser-search commands anymore; they are answered by the AI.

OpenAI is preferred. Gemini is supported as an alternative. If the AI provider is temporarily unavailable, the app attempts free knowledge fallbacks rather than pretending it has answered with AI.

## Troubleshooting

Open `http://localhost:5000/api/ai-status`. `ready_for_general_ai` must be true for full AI answering.
