from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./student_management.db")
    secret_key: str = os.getenv(
        "SECRET_KEY", "development-only-change-this-secret-key"
    )
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
    auto_seed: bool = _as_bool(os.getenv("AUTO_SEED", "true"))


settings = Settings()
