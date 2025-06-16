from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    class Config:
        env_file = ".env"

    TAVILY_API_KEY: str
    GOOGLE_API_KEY: str
    GOOGLE_GENAI_USE_VERTEXAI: bool
    GOOGLE_CLOUD_PROJECT_ID: str

    # Service account credentials as JSON string
    GOOGLE_SERVICE_ACCOUNT_JSON: Optional[str] = None

    RENDERER_SERVICE_URL: str

    OPENAI_API_KEY: str

    PEXELS_API_KEY: str


settings = Settings()
