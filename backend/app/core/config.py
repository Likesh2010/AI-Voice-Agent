import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    app_name: str = "Voice Recruitment Agent"
    database_url: str = Field("sqlite:///./voice_recruitment.db")
    openai_api_key: str = Field("")
    openai_response_model: str = Field("gpt-4.1-mini")
    openai_tts_model: str = Field("gpt-4o-mini-tts")
    openai_stt_model: str = Field("whisper-1")
    twilio_account_sid: str = Field("")
    twilio_auth_token: str = Field("")
    twilio_phone_number: str = Field("")
    public_base_url: str = Field("")


# Allow a development fallback if OPENAI_API_KEY isn't set yet so the app can be run locally for testing.
if not os.environ.get("OPENAI_API_KEY"):
    # Do not set a real key here — this is only to allow local startup. Replace with your key in backend/.env
    os.environ.setdefault("OPENAI_API_KEY", "test")

settings = Settings()
