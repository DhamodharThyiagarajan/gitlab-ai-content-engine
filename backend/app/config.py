from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "GitLab AI Content Engine"
    app_env: str = "development"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    database_url: str = "sqlite:///./gitlab_ai_content.db"
    firebase_project_id: str = ""
    firebase_service_account_json: str = ""
    firebase_service_account_path: str = ""
    auth_provider: str = "firebase"
    jwt_secret: str = "change-me"
    jwt_expire_minutes: int = 1440
    ai_provider: str = "mock"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4.1-mini"
    ai_timeout_seconds: int = 120
    gitlab_url: str = "https://gitlab.com"
    gitlab_token: str = ""
    gitlab_project_id: str = ""
    cors_origins: str = "http://localhost:3000"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

settings = Settings()
