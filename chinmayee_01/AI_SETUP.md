# Nova Voice Assistant - AI setup

This app can perform local commands and answer general questions through an AI provider.
For ChatGPT-like general answers, you must configure an API key. The key is kept locally in `.env` and is not included in this ZIP.

## Recommended: OpenAI

1. Copy `.env.example` to `.env`.
2. Put your API key on this line:

`OPENAI_API_KEY=your_key_here`

3. Keep:

`USE_LLM_FALLBACK=true`

4. The default model is `gpt-5.6-luna`.
5. Restart `run_web.bat` after changing `.env`.

You can also run `setup_ai.bat` to enter the key interactively.

## Test the server

Open these URLs after starting the app:

- http://localhost:5000/api/health
- http://localhost:5000/api/ai-status

`ready_for_general_ai` should be `true` when an API key is loaded.

## Important

No local program can guarantee a correct answer to literally every possible question. With a general-purpose AI model and web search, however, this app can handle a very broad range of questions and current-information requests. Important facts should still be verified.
