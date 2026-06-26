from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-5"
    openai_embedding_model: str = "text-embedding-3-small"
    database_url: str = "sqlite:///./chat_history.db"
    cors_origins: list[str] = ["http://localhost:3000"]
    supabase_url: str = ""
    supabase_key: str = ""
    rrf_match_count: int = 8
    rrf_k: int = 50


settings = Settings()
