# Dash Movers Voice Agent

This project provides a real-time voice customer service agent for a moving company using FastAPI, Twilio ConversationRelay, OpenAI, and ElevenLabs.

## Development

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Copy `example.toml` to `.streamlit/secrets.toml` and fill in your credentials. The application reads settings via `st.secrets` or environment variables.
