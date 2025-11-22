# Stage 1: Build stage for installing dependencies
FROM python:3.10-slim as builder

# Install system dependencies required for whisper (ffmpeg) and other libraries.
# Using --no-install-recommends keeps the image lean.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set up a non-root user and a virtual environment for isolation and security.
RUN useradd --create-home appuser
ENV VIRTUAL_ENV=/home/appuser/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy and install Python requirements as the non-root user.
WORKDIR /home/appuser/app
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt



# Set the PATH to use the virtual environment's python.
ENV PATH="/home/appuser/venv/bin:$PATH"

# Set working directory and switch to the non-root user.
WORKDIR /home/appuser
USER appuser

# Copy application code and migration scripts.
COPY --chown=appuser:appuser ./app ./app
COPY --chown=appuser:appuser alembic.ini .
COPY --chown=appuser:appuser alembic ./alembic

# Expose the port the app runs on.
EXPOSE 8000

# On container start, run database migrations and then launch the application with Gunicorn.
# Gunicorn acts as a process manager, and we use Uvicorn workers for ASGI.
# The web process binds to $PORT, which is standard for most PaaS providers.
# We use a single worker to keep memory usage low on free tiers.
CMD ["sh", "-c", "alembic upgrade head && gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT"]
