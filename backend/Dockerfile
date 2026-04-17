# syntax=docker/dockerfile:1.7
# ---- Build stage ----
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System deps pro faster-whisper (ffmpeg) + build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        ffmpeg \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalace závislostí
COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install -e . --no-deps && \
    pip install \
        fastapi>=0.115.0 \
        "uvicorn[standard]>=0.32.0" \
        websockets>=13.1 \
        python-multipart>=0.0.17 \
        pydantic>=2.9 \
        pydantic-settings>=2.6 \
        sqlalchemy>=2.0.36 \
        alembic>=1.14.0 \
        aiosqlite>=0.20.0 \
        chromadb>=0.5.20 \
        sentence-transformers>=3.3.1 \
        claude-agent-sdk>=0.1.0 \
        apscheduler>=3.10.4 \
        httpx>=0.28.0 \
        trafilatura>=1.12.2 \
        feedparser>=6.0.11 \
        selectolax>=0.3.27 \
        google-auth>=2.36.0 \
        google-auth-oauthlib>=1.2.1 \
        google-api-python-client>=2.153.0 \
        yt-dlp>=2024.11.0 \
        faster-whisper>=1.1.0 \
        ffmpeg-python>=0.2.0 \
        pypdf>=5.1.0 \
        python-docx>=1.1.2 \
        pdfplumber>=0.11.4 \
        cryptography>=43.0.3 \
        "passlib[bcrypt]>=1.7.4" \
        python-dotenv>=1.0.1 \
        loguru>=0.7.2 \
        orjson>=3.10.12

# ---- Runtime stage ----
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && adduser --disabled-password --gecos "" --uid 1000 app

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY app ./app
RUN mkdir -p data/chroma data/reference_articles data/articles/drafts \
             data/articles/published data/transcripts data/video_scripts \
             data/uploads && \
    chown -R app:app /app

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
