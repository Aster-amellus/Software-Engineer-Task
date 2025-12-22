import os
from functools import lru_cache

try:
    from pydantic import BaseSettings, Field
except ImportError:  # pragma: no cover - fallback for minimal test envs
    BaseSettings = None
    Field = None


if BaseSettings:

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

        class Config:
            env_file = ".env"
            case_sensitive = False


else:

    class Settings:
        def __init__(self):
            self.app_name = "Arxiv Review System"
            self.environment = os.getenv("APP_ENV", "dev")
            self.log_level = os.getenv("LOG_LEVEL", "INFO")
            self.database_url = os.getenv(
                "DATABASE_URL", "postgresql+psycopg://postgres:postgres@db:5432/arxiv_review"
            )
            self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
            self.chroma_dir = os.getenv("CHROMA_DIR", "/data/chroma")
            self.storage_root = os.getenv("STORAGE_ROOT", "/data/storage")
            self.jwt_secret = os.getenv("JWT_SECRET", "dev-secret")
            self.jwt_algorithm = "HS256"
            self.access_token_expire_minutes = 60 * 24
            self.llm_provider = os.getenv("LLM_PROVIDER", "mock")
            self.embed_provider = os.getenv("EMBED_PROVIDER", "mock")
            self.openai_base_url = os.getenv("OPENAI_COMPAT_BASE_URL", "")
            self.openai_api_key = os.getenv("OPENAI_COMPAT_API_KEY", "")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
