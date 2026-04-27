from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Health Metrics API"
    debug: bool = True
    database_url: str = "sqlite:///./database/app.db"
    deepseek_api_key: str | None = None
    deepseek_base_url: str = "https://api.deepseek.com/chat/completions"
    deepseek_model: str = "deepseek-chat"
    deepseek_timeout_seconds: float = 60.0

    class Config:
        env_file = ".env"

settings = Settings()
