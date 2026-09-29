import logging
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import init_db
from routers.auth_routes import router as auth_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLAlchemy database tables on startup
    logger.info("Initializing SQLAlchemy ORM models & database tables...")
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI backend with SQLAlchemy ORM integrating Firebase Auth & Supabase Database",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)

@app.get("/")
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "FastAPI Backend API with SQLAlchemy ORM is running",
        "database_url": settings.sqlalchemy_database_url.split("@")[-1] if "@" in settings.sqlalchemy_database_url else settings.sqlalchemy_database_url
    }

if __name__ == "__main__":
    logger.info(f"Starting FastAPI server on port {settings.PORT}...")
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
