# Dash Movers Voice Agent

This project provides a real-time voice customer service agent for a moving company using FastAPI, Twilio ConversationRelay, OpenAI, and ElevenLabs.

## Development

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Copy `example.toml` to `.streamlit/secrets.toml` and fill in your credentials. The application reads settings exclusively from Streamlit secrets both locally and on Streamlit Community Cloud.

Your `.streamlit/secrets.toml` should include entries for all of the provider keys used by the app, for example:

```toml
OPENAI_API_KEY = "sk-..."
DATABASE_URL = "postgresql+psycopg://user:pass@localhost/db"

# Twilio
TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN = "your-auth-token"
TWILIO_NUMBER = "+15555551234"
TWILIO_FORWARD_NUMBER = "+15555559876"

# Email + voice
AWS_SES_REGION = "us-east-1"
AWS_SES_ACCESS_KEY_ID = "your-aws-access-key-id"
AWS_SES_SECRET_ACCESS_KEY = "your-aws-secret-access-key"
# Optional: provide a configuration set name if you use one
AWS_SES_CONFIGURATION_SET = ""
FROM_EMAIL = "no-reply@example.com"
ELEVENLABS_VOICE_ID = "your-voice-id"

BASE_URL = "https://your-app-url.com"
WS_URL = "wss://your-app-url.com/voice/ws"  # optional override
COMPANY_NAME = "Dash Movers"
COMPANY_CITY = "Your City"
```

When running the FastAPI app outside of Streamlit, the configuration loader will read from `.streamlit/secrets.toml` directly, so no environment variables are required.
