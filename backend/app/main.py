"""Application entrypoint.

Centralized settings + structured logging + background maintenance tasks.
"""
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from app.routes import speech_routes, resume_routes, chat_routes, bot_routes
from app.auth import auth_routes
from app.database.db import Base, engine, SessionLocal
import logging
import json
import threading
import time
from app.core.settings import settings
from app.database import crud
from app.middleware.rate_limit import limiter, _rate_limit_exceeded_handler
from fastapi import Request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "ts": record.created,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            log_record["exc"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

for handler in logging.getLogger().handlers:
    handler.setFormatter(JsonFormatter())

app = FastAPI(title="Speech Analysis API", version="v1", openapi_tags=[
    {"name": "auth", "description": "Authentication & token management"},
    {"name": "speech", "description": "Speech upload & transcription"},
    {"name": "resume", "description": "Resume parsing services"},
    {"name": "chat", "description": "Chat history operations"},
])

# Attach rate limiting
app.state.limiter = limiter
app.add_exception_handler(Exception, _rate_limit_exceeded_handler)

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["path"])

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    path = request.url.path
    method = request.method
    with REQUEST_LATENCY.labels(path=path).time():
        response = await call_next(request)
    REQUEST_COUNT.labels(method=method, path=path, status=response.status_code).inc()
    return response

# Create database tables on startup
@app.on_event("startup")
def startup():
    """Ensures all database tables are created when the application starts."""
    Base.metadata.create_all(bind=engine)
    logging.info("Database tables created/checked.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_allow_origins.split(',')],
    allow_credentials=True,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Include routers
app.include_router(auth_routes.router, prefix="/api/auth", tags=["auth"])
app.include_router(speech_routes.router, prefix="/api/speech", tags=["speech"])
app.include_router(resume_routes.router, prefix="/api/resume", tags=["resume"])
app.include_router(chat_routes.router, prefix="/api/chat", tags=["chat"])
app.include_router(bot_routes.router, prefix="/api/bot", tags=["bot"])

@app.get("/")
async def root():
    """Root endpoint for the API."""
    return {"message": "Speech Analysis API is running", "version": app.version}

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


def _blacklist_cleanup_loop(interval_seconds: int = 3600):
    """Background loop to remove expired blacklisted tokens periodically."""
    logging.getLogger(__name__).info("Blacklist cleanup thread started")
    while True:
        try:
            db = SessionLocal()
            crud.remove_expired_blacklisted_tokens(db)
            db.close()
            logging.getLogger(__name__).info("Expired blacklisted tokens purged")
        except Exception as e:
            logging.getLogger(__name__).error(f"Blacklist cleanup error: {e}")
        time.sleep(interval_seconds)

@app.on_event("startup")
def start_background_jobs():
    # Start cleanup in separate daemon thread
    t = threading.Thread(target=_blacklist_cleanup_loop, daemon=True)
    t.start()
    # Telemetry (OpenTelemetry/Sentry) removed per user request

