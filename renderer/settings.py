from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    
    class Config:
        env_file = ".env"
    
    PORT: int
    ALLOWED_ORIGINS: List[str]
    

settings = Settings()
