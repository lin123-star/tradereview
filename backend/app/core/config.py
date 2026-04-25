from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # 数据库
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/tradereview.db"

    # AI API
    GEMINI_API_KEY: str = ""
    KIMI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # 代理（Gemini需要）
    PROXY_URL: str = "http://127.0.0.1:7897"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_file = BASE_DIR / ".env"
        extra = "ignore"


settings = Settings()
