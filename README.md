# Roster AI

Roster is a modular Windows personal AI assistant with voice input, text fallback, multi-step tool execution, memory, screen understanding, controlled computer actions, and interchangeable AI providers.

## AI providers

Roster supports Groq, Gemini, xAI/Grok, and Claude. Select the primary provider with ROSTER_PROVIDER and optional failover providers with ROSTER_PROVIDER_FALLBACKS.

Provider keys are environment secrets and must never be committed.

## Provider examples

`python main.py --list-providers`

`python main.py --provider gemini --input text`

`python main.py --provider claude --input text`

`python main.py --provider xai --input text`

`python main.py --provider groq --input auto`

Auto input uses microphone transcription when Groq is configured; otherwise it uses text input.

## Install and run

`python -m pip install -r requirements.txt`

`python main.py`

## Architecture

Roster includes core agent orchestration, SQLite memory, permissions, tracing, cancellation, file tools, computer controls, browser safety, tasks, scheduler primitives, provider routing, and diagnostics.

## Security

API keys come from environment variables. Side-effecting tools require confirmation. File tools are scoped to approved roots. Browser access rejects local/private/reserved network targets. File and screenshot content is treated as data, not instructions.

## Development

`python -m compileall roster`

`pytest -q`
