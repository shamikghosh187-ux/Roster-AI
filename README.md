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

## Wake word

When voice mode and Groq transcription are configured, Roster defaults to a hands-free wake-word flow. Start Roster normally, and it waits quietly for **“Hey Roster”** before speaking and entering the full assistant loop.

The behavior is controlled by:

- `ROSTER_WAKE_MODE=auto` — enable wake mode automatically for voice input.
- `ROSTER_WAKE_MODE=on` — force wake mode when voice input is available.
- `ROSTER_WAKE_MODE=off` — start the assistant immediately.
- `ROSTER_WAKE_WORD=hey roster` — customize the phrase.
- `ROSTER_WAKE_CHUNK_SECONDS=2.5` — microphone chunk size.
- `ROSTER_WAKE_COOLDOWN_SECONDS=0.5` — cooldown after activation.

CLI examples:

`python main.py --input voice --wake on`

`python main.py --input voice --wake off`

The wake listener reuses Roster's existing Groq transcription path, removes each temporary audio chunk after transcription, and does not send audio anywhere else. A fully closed Roster process still needs to be launched by Windows Startup/Task Scheduler if you want the machine to listen for the phrase after login.

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


## Desktop workspace

Roster includes an optional Qt desktop workspace with persistent conversation history, provider switching, background execution, live trace inspection, cancellation, and GUI-thread permission confirmation.

Install the desktop layer with: `python -m pip install -r requirements-desktop.txt`

Launch it with: `python main.py --ui`

The CLI remains available with: `python main.py`

## Production diagnostics

Roster includes a dependency-light diagnostic command for installation and configuration checks:

`python main.py --doctor`

The doctor reports configuration issues, dependency availability, and which provider credentials are configured **without printing credential values**. Runtime health primitives are also available to integration layers through `roster.health` and `roster.runtime_health`.

### Production runtime principles

- Preserve existing public runtime APIs when adding infrastructure.
- Keep secrets out of diagnostics and telemetry.
- Prefer explicit health/readiness signals over implicit startup assumptions.
- Keep metrics thread-safe and dependency-light.
- Keep provider, audio, UI, and computer integrations behind composition boundaries.
