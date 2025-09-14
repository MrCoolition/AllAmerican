import os

try:
    import streamlit as st
    _secrets = st.secrets
except Exception:  # pragma: no cover - streamlit not available
    _secrets = {}


def _get(key: str, default: str | None = None) -> str | None:
    return _secrets.get(key) or os.getenv(key) or default


class Settings:
    OPENAI_API_KEY = _get("OPENAI_API_KEY")
    DATABASE_URL = _get("DATABASE_URL")
    TWILIO_ACCOUNT_SID = _get("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = _get("TWILIO_AUTH_TOKEN")
    TWILIO_NUMBER = _get("TWILIO_NUMBER")
    TWILIO_FORWARD_NUMBER = _get("TWILIO_FORWARD_NUMBER")
    SENDGRID_API_KEY = _get("SENDGRID_API_KEY")
    FROM_EMAIL = _get("FROM_EMAIL")
    BASE_URL = _get("BASE_URL")
    WS_URL = _get("WS_URL") or (BASE_URL or "").replace("https", "wss") + "/voice/ws"
    ELEVENLABS_VOICE_ID = _get("ELEVENLABS_VOICE_ID", "UgBBYS2sOqTuMpoF3BR0")
    COMPANY_NAME = _get("COMPANY_NAME", "Dash Movers")
    COMPANY_CITY = _get("COMPANY_CITY", "Your City")


settings = Settings()
