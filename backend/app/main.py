from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from app.config import settings
from app.db.session import Base, engine
from app.api import auth, content_jobs, reviews, publishing, metrics

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix="/api")
app.include_router(content_jobs.router, prefix="/api")
app.include_router(content_jobs.jobs_router, prefix="/api")
app.include_router(reviews.router, prefix="/api")
app.include_router(publishing.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": settings.app_name}


@app.get("/health/ready", tags=["health"])
def readiness():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ready", "database": "connected"}


@app.on_event("startup")
def initialize_database():
    # Create current tables, then apply the one additive migration needed for
    # databases created before Firebase UID support was added.
    Base.metadata.create_all(bind=engine)
    user_columns = {column["name"] for column in inspect(engine).get_columns("users")}
    if "firebase_uid" not in user_columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE users ADD COLUMN firebase_uid VARCHAR(128)"))
            connection.execute(
                text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_firebase_uid ON users (firebase_uid)")
            )

