import os

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    # RAG/Vector/LLM settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    GROQ_API_KEY: str = ""
    CHROMA_PERSIST_DIRECTORY: str = ".chroma"
    CHROMA_SERVER_HOST: str = "localhost"
    CHROMA_SERVER_PORT: int = 8001
    RAG_COLLECTION_NAME: str = "wp_codex_plugin"
    # CORS settings
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(levelname)s: (%(asctime)s) (%(name)s) %(message)s"
    LOG_FILE: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class TestConfig(Config):
    __test__ = False  # Prevent pytest from collecting this as a test class


class LocalConfig(Config):
    ...


class ProductionConfig(Config):
    DEBUG: bool = False
    CORS_ORIGINS: str = "https://yourdomain.com,https://www.yourdomain.com"
    LOG_LEVEL: str = "WARNING"
    LOG_FILE: str = "app.log"


def get_config() -> Config:
    env = os.getenv("ENV", "local")
    config_type = {
        "test": TestConfig(),
        "local": LocalConfig(),
        "prod": ProductionConfig(),
    }
    return config_type[env]


config: Config = get_config()
