import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
env_local_path = Path(__file__).parent.parent / "frontend" / ".env.local"

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
elif env_local_path.exists():
    load_dotenv(dotenv_path=env_local_path)
else:
    load_dotenv()

class Settings:
    PROJECT_NAME: str = "GitLab AI Content Engine Backend (FastAPI + SQLAlchemy)"
    PORT: int = int(os.getenv("PORT", "5000"))
    
    # Database URL for SQLAlchemy (Supabase PostgreSQL or fallback SQLite)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        os.getenv("SUPABASE_DB_URL", "sqlite:///./app.db")
    )
    
    @property
    def sqlalchemy_database_url(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    # Raw Supabase API Credentials
    RAW_SUPABASE_URL: str = os.getenv("SUPABASE_URL", os.getenv("NEXT_PUBLIC_SUPABASE_URL", ""))
    SUPABASE_KEY: str = os.getenv(
        "SUPABASE_KEY",
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", ""))
    )
    
    # Clean Supabase URL (strips trailing /rest/v1 or trailing slashes automatically)
    @property
    def SUPABASE_URL(self) -> str:
        url = self.RAW_SUPABASE_URL.strip()
        if url.endswith("/"):
            url = url.rstrip("/")
        if url.endswith("/rest/v1"):
            url = url[:-8].rstrip("/")
        return url

    # Firebase Service Account Path
    FIREBASE_SERVICE_ACCOUNT_PATH: str = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_PATH",
        str(Path(__file__).parent / "serviceAccountKey.json")
    )
    
    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
        "http://127.0.0.1:8000",
        "*"
    ]

settings = Settings()
    
