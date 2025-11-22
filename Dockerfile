# Stage 1: Build stage for installing dependencies
FROM python:3.11-slim as builder

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

# Pre-download the Whisper model to avoid runtime downloads.
# The model size should match the WHISPER_MODEL_SIZE in your .env file.
# Defaulting to 'small'. Change this if you use a different size.
ARG WHISPER_MODEL_SIZE=small
RUN python -c "import whisper; whisper.load_model('$WHISPER_MODEL_SIZE', download_root='/home/appuser/.cache/whisper')"


# Stage 2: Final production image
FROM python:3.11-slim as final

# Install ffmpeg, which is a runtime dependency for whisper.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user.
RUN useradd --create-home appuser

# Copy the virtual environment from the builder stage.
COPY --from=builder --chown=appuser:appuser /home/appuser/venv /home/appuser/venv
# Copy the pre-downloaded whisper model
COPY --from=builder --chown=appuser:appuser /home/appuser/.cache/whisper /home/appuser/.cache/whisper

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

# On container start, run database migrations and then launch the application.
# This ensures the database is up-to-date before the app starts serving requests.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
