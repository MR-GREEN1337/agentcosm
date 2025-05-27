from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = ".env"

    TAVI_API_KEY: str
    GOOGLE_API_KEY: str
    GOOGLE_GENAI_USE_VERTEXAI: bool


settings = Settings()
