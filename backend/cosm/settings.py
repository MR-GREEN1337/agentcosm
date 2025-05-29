from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = ".env"

    TAVILY_API_KEY: str
    GOOGLE_API_KEY: str
    GOOGLE_GENAI_USE_VERTEXAI: bool
    GOOGLE_CLOUD_PROJECT_ID: str

    RENDERER_SERVICE_URL: str

    GROQ_API_KEY: str
    OPENAI_API_KEY: str


settings = Settings()
