# Roster AI

Roster is a modular Windows personal AI assistant with voice input, text fallback, multi-step tool execution, memory, screen understanding, controlled computer actions, and interchangeable AI providers.

## AI providers

Roster has adapters for **13 providers**:

- Groq
- Google Gemini
- xAI / Grok
- Anthropic Claude
- OpenRouter
- DeepSeek
- Mistral
- Together AI
- Fireworks AI
- Cerebras
- SambaNova
- Perplexity
- NVIDIA NIM

Select the primary provider with `ROSTER_PROVIDER` and configure ordered failover providers with comma-separated `ROSTER_PROVIDER_FALLBACKS`. Provider keys are environment secrets and must never be committed.

The nine OpenAI-compatible adapters use their provider's own API endpoint and key. Their default model can be overridden with `ROSTER_OPENROUTER_MODEL`, `ROSTER_DEEPSEEK_MODEL`, `ROSTER_MISTRAL_MODEL`, `ROSTER_TOGETHER_MODEL`, `ROSTER_FIREWORKS_MODEL`, `ROSTER_CEREBRAS_MODEL`, `ROSTER_SAMBANOVA_MODEL`, `ROSTER_PERPLEXITY_MODEL`, or `ROSTER_NVIDIA_MODEL`. Model availability and account access depend on each provider; override the default if it is not enabled for your account.

API key environment variables:

| Provider | Environment variable |
|---|---|
| Groq | `GROQ_API_KEY` |
| Gemini | `GEMINI_API_KEY` |
| xAI | `XAI_API_KEY` |
| Claude | `ANTHROPIC_API_KEY` |
| OpenRouter | `OPENROUTER_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` |
| Mistral | `MISTRAL_API_KEY` |
| Together AI | `TOGETHER_API_KEY` |
| Fireworks AI | `FIREWORKS_API_KEY` |
| Cerebras | `CEREBRAS_API_KEY` |
| SambaNova | `SAMBANOVA_API_KEY` |
| Perplexity | `PERPLEXITY_API_KEY` |
| NVIDIA NIM | `NVIDIA_API_KEY` |

Provider adapters currently cover text chat, intent planning, and workflow planning where the adapter implements them. **Voice transcription remains on the existing Groq/Whisper path**; the new text providers are not advertised as speech providers. Vision support also remains capability-specific rather than being assumed for every adapter.

## Provider examples

`python main.py --list-providers`

`python main.py --provider gemini --input text`

`python main.py --provider claude --input text`

`python main.py --provider xai --input text`

`python main.py --provider openrouter --input text`

`python main.py --provider deepseek --input text`

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
- `ROSTER_RECORD_SECONDS=20` — maximum capture window per utterance; adaptive silence detection normally ends recording earlier.
- `ROSTER_TTS_RATE=185` — speech rate for the built-in voice.
- `ROSTER_TTS_VOLUME=1.0` — built-in speech volume from 0.0 to 1.0.
- `ROSTER_NOISE_GATE=400` — input amplitude threshold for speech detection.
- `ROSTER_VOICE_RUNTIME=1` — opt into the newer bounded voice runtime, normalized audio frames, and interruptible TTS lifecycle. Leave unset to use the existing voice loop.

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

Roster includes an optional Qt desktop workspace with:

- Conversation view with background execution, provider switching, trace inspection, and cancellation.
- **Memory** browser for reviewing and deleting saved long-term memories.
- **Tools** catalog showing each registered tool's description, confirmation requirement, and retry-safety flag, with per-session enable/disable checkboxes. Disabled tools are blocked by the runtime, not just hidden in the UI.
- **Tasks** view with runtime counters and the recent execution trace.
- **Diagnostics** view showing dependency/configuration checks and provider credential presence without exposing credential values.
- GUI-thread permission dialogs for sensitive actions.

Install the desktop layer with: `python -m pip install -r requirements-desktop.txt`

Launch it with: `python main.py --ui`

The CLI remains available with: `python main.py`

## Production diagnostics

Roster includes a diagnostic command for installation and configuration checks:

`python main.py --doctor`

The doctor reports configuration issues, dependency availability, and which provider credentials are configured **without printing credential values**. Runtime health primitives are also available to integration layers through `roster.health` and `roster.runtime_health`.

### Production runtime principles

- Preserve existing public runtime APIs when adding infrastructure.
- Keep secrets out of diagnostics and telemetry.
- Prefer explicit health/readiness signals over implicit startup assumptions.
- Keep metrics thread-safe and dependency-light.
- Keep provider, audio, UI, and computer integrations behind composition boundaries.


## Windows application bundle (early access)

ROSTER is a local Windows application, not a Vercel web function. Its microphone, speakers, wake-word listener, and computer-control features must run on the PC that owns those devices. Vercel is not the deployment target for the desktop assistant.

### Build a portable folder

Use Windows PowerShell from a fresh checkout. Python 3.11 is the recommended build environment for the first packaged builds:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\build_windows.ps1
```

The script creates `dist\ROSTER\ROSTER.exe` and its supporting files. This is an **on-directory portable bundle**, not an installer. Keep the whole `dist\ROSTER` folder together when moving it to another PC.

Start with the diagnostic commands:

```powershell
.\dist\ROSTER\ROSTER.exe --list-providers
.\dist\ROSTER\ROSTER.exe --doctor
```

### Configure secrets locally

Create a private `.env` file in the project working directory when running from source, or configure the relevant environment variables in the Windows user environment when using the portable bundle. Do not put API keys in source control, build scripts, release artifacts, or the executable. Never send a filled `.env` file when asking for help.

The packaged build does not include your API keys, saved memory, or personal configuration. Provider access still depends on your own API account and selected model. Microphone and speaker behavior must be validated on the target Windows machine.

### Automated Windows build

The Windows Packaging workflow runs on pull requests and pushes to `main`, and can also be started manually from GitHub Actions. It runs a packaged CLI smoke check and uploads the portable folder as a workflow artifact. The artifact is for validation and testing; it is not yet a signed installer or a public production release.

**Important:** CI can verify that the bundle builds and that its CLI starts. It cannot prove microphone permissions, wake-word accuracy, echo handling, or speaker playback on your specific hardware. Those require a real-device test.
