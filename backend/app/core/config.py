import os
from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "Arxiv Review System"
    environment: str = Field("dev", env="APP_ENV")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    database_url: str = Field(
        "postgresql+psycopg://postgres:postgres@db:5432/arxiv_review",
        env="DATABASE_URL",
    )
    redis_url: str = Field("redis://redis:6379/0", env="REDIS_URL")
    chroma_dir: str = Field("/data/chroma", env="CHROMA_DIR")
    storage_root: str = Field("/data/storage", env="STORAGE_ROOT")

    jwt_secret: str = Field("dev-secret", env="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    llm_provider: str = Field("mock", env="LLM_PROVIDER")
    embed_provider: str = Field("mock", env="EMBED_PROVIDER")
    openai_base_url: str = Field("", env="OPENAI_COMPAT_BASE_URL")
    openai_api_key: str = Field("", env="OPENAI_COMPAT_API_KEY")
    coze_base_url: str = Field("", env="COZE_BASE_URL")
    coze_api_key: str = Field("", env="COZE_API_KEY")
    coze_model: str = Field("coze-default", env="COZE_MODEL")

    task_always_eager: bool = Field(False, env="CELERY_TASK_ALWAYS_EAGER")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
