from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    bot_token: str
    supabase_url: str
    supabase_key: str
    daily_summary_hour: int = 21
    daily_summary_minute: int = 0


config = Config()
