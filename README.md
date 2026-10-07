# 🎙️ Roster AI Assistant

Roster is a modular Windows personal AI assistant built with Python.

## Capabilities

- Voice input and text-to-speech
- AI conversation and multi-step planning
- Persistent local conversation memory
- Screen vision
- Windows application launching
- Controlled desktop interaction
- Local file listing and reading
- Text search across local files
- Google and YouTube actions
- WhatsApp messaging with confirmation

## Run

```bash
git clone https://github.com/shamikghosh187-ux/Roster-AI.git
cd Roster-AI
python -m pip install -r requirements.txt
python main.py
```

Set `GROQ_API_KEY` before running.

## Security

Roster requires confirmation before side-effecting desktop, app-launch, and messaging actions. Content discovered in files or screenshots is treated as data, not as user instructions.
