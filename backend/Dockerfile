# syntax=docker/dockerfile:1.7
# ---- Build stage (Python deps) ----
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        ffmpeg \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install -e . --no-deps --no-cache-dir

# PyTorch CPU-only (ušetří ~2 GB)
RUN pip install --no-cache-dir \
        --index-url https://download.pytorch.org/whl/cpu \
        torch>=2.5.0

RUN pip install --no-cache-dir \
        fastapi>=0.115.0 \
        "uvicorn[standard]>=0.32.0" \
        websockets>=13.1 \
        python-multipart>=0.0.17 \
        pydantic>=2.9 \
        "pydantic[email]>=2.9" \
        email-validator>=2.2.0 \
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

RUN rm -rf /root/.cache/pip /tmp/*

# ---- Runtime stage ----
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/usr/local/bin:/usr/bin:/bin"

# System packages + Node.js 22 (pro Claude Code CLI)
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        curl \
        ca-certificates \
        gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
        | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" \
        > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update && apt-get install -y --no-install-recommends nodejs \
    && npm install -g @anthropic-ai/claude-code \
    && rm -rf /var/lib/apt/lists/* /root/.npm

# Vytvoř user `app` (UID 1000) přímou editací /etc/passwd — obejdeme problém,
# že python:3.11-slim neobsahuje `useradd` ani v PATH, ani v expected location.
RUN echo 'app:x:1000:1000::/home/app:/bin/bash' >> /etc/passwd \
    && echo 'app:x:1000:' >> /etc/group \
    && mkdir -p /home/app \
    && chown 1000:1000 /home/app

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY app ./app
RUN mkdir -p data/chroma data/reference_articles data/articles/drafts \
             data/articles/published data/transcripts data/video_scripts \
             data/uploads \
    && chown -R 1000:1000 /app /home/app

# Kontejner běží jako non-root (UID 1000 = user 'app'). Důvod:
# Claude Code CLI blokuje --dangerously-skip-permissions pro root uživatele
# ("security reasons"). Mounty z hostu musí být chown -R 1000:1000 aby měl
# container přístup — viz scripts/fix-claude-permissions.sh.
USER app
ENV HOME=/home/app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
