from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Health Metrics API"
    debug: bool = True
    database_url: str = "sqlite:///./database/app.db"
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_api_key: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
