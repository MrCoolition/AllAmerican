from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

try:
    import streamlit as st

    _secrets_source: Mapping[str, Any] = st.secrets
except Exception:  # pragma: no cover - streamlit not available
    _secrets_source = {}


def _load_local_secrets(path: Path) -> Mapping[str, Any]:
    if not path.exists():
        return {}

    try:
        try:  # Python >=3.11
            import tomllib  # type: ignore[attr-defined]
        except ModuleNotFoundError:  # pragma: no cover - fallback for <3.11
            import tomli as tomllib  # type: ignore[import-not-found]
    except ModuleNotFoundError:  # pragma: no cover - tomli not installed
        return {}

    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except Exception:  # pragma: no cover - optional local fallback
        return {}


if not _secrets_source:
    _secrets_source = _load_local_secrets(Path(".streamlit/secrets.toml"))


def _get(key: str, default: str | None = None) -> str | None:
    value = _secrets_source.get(key)
    return value if value not in (None, "") else default


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
