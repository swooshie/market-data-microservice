from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "market-data-service"
    api_v1_prefix: str = "/"
    provider: str = "alpha_vantage"      # default
    alpha_vantage_api_key: str | None = None
    # db, kafka, redis urls will come later

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()  # singleton