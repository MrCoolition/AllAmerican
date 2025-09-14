import os

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
    TWILIO_FORWARD_NUMBER = os.getenv("TWILIO_FORWARD_NUMBER")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    FROM_EMAIL = os.getenv("FROM_EMAIL")
    BASE_URL = os.getenv("BASE_URL")
    WS_URL = os.getenv("WS_URL") or os.getenv("BASE_URL", "").replace("https", "wss") + "/voice/ws"
    ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "UgBBYS2sOqTuMpoF3BR0")
    COMPANY_NAME = os.getenv("COMPANY_NAME", "Dash Movers")
    COMPANY_CITY = os.getenv("COMPANY_CITY", "Your City")

settings = Settings()
