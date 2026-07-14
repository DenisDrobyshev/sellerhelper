"""Application settings, loaded from environment / .env (see .env.example)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "SellerCompass"

    database_url: str = (
        "postgresql+asyncpg://sellercompass:sellercompass@localhost:5434/sellercompass"
    )
    redis_url: str = "redis://localhost:6381/0"

    # LLM — bring your own key in the open-source build.
    llm_api_key: str = ""
    llm_model: str = ""

    # Wildberries collector.
    wb_proxy_url: str = ""
    wb_requests_per_second: float = 0.5
    wb_search_version: str = "v9"
    wb_dest: int = -1257786


@lru_cache
def get_settings() -> Settings:
    return Settings()
