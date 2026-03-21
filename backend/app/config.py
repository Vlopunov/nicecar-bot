from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Telegram
    BOT_TOKEN: str = ""
    WEBAPP_URL: str = "http://localhost:5173"
    ADMIN_IDS: str = ""
    ADMIN_CHAT_ID: int = 0

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://nicecar:nicecar@localhost:5432/nicecar"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Instagram
    INSTAGRAM_SESSION_ID: str = ""
    INSTAGRAM_USERNAME: str = "nicecar.center"

    # App
    SECRET_KEY: str = "change-me"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Loyalty
    CASHBACK_PERCENT: int = 5
    REFERRAL_BONUS: int = 50
    REFERRAL_WELCOME_BONUS: int = 20
    MAX_BONUS_USAGE_PERCENT: int = 20
    BONUS_EXPIRY_MONTHS: int = 6

    @property
    def admin_ids_list(self) -> List[int]:
        if not self.ADMIN_IDS:
            return []
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
