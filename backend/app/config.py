from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    google_api_key: str = ""
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    model_name: str = "claude-sonnet-4-20250514"
    max_retries: int = 3

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
