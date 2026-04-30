from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Health Metrics API"
    debug: bool = True
    database_url: str = "sqlite:////app/database/app.db"
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_api_key: str = ""
    secret_key: str = ""
    admin_username: str = "admin"
    admin_password: str = "zhouyou123"
    access_token_expires_minutes: int = 10080
    login_lock_max_failures: int = 3
    login_lock_minutes: int = 30

    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }

settings = Settings()
