from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Chongqing Training Program Agent API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS Configuration
    CORS_ORIGINS: list = ["*"]

    # DeepSeek Configuration
    DEEPSEEK_API_KEY: str = "sk-f064befbb5a749399fbf81e68d1e2c38"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat" # upgraded to DeepSeek-V3.2

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
