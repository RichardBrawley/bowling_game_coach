# syntax=docker/dockerfile:1.7
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=180

# 1) Install CPU-only torch first from the PyTorch CPU index (as root)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu \
    "torch==2.8.0+cpu"

# 2) Install all remaining deps with valid pip specifiers (as root)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir \
    "fastapi>=0.118.0,<0.119.0" \
    "uvicorn>=0.37.0,<0.38.0" \
    "sqlalchemy>=2.0.43,<3.0.0" \
    "sqlalchemy-utils>=0.42.0,<0.43.0" \
    "pgvector>=0.4.1,<0.5.0" \
    "psycopg2-binary" \
    "passlib[bcrypt]>=1.7.4,<2.0.0" \
    "bcrypt==3.2.2" \
    "python-jose[cryptography]>=3.5.0,<4.0.0" \
    "haystack-ai>=2.18.1,<3.0.0" \
    "pgvector-haystack>=5.2.1,<6.0.0" \
    "openai>=2.0.1,<3.0.0" \
    "transformers>=4.56.2,<5.0.0" \
    "sentence-transformers>=5.1.1,<6.0.0" \
    "python-multipart>=0.0.20,<0.0.21" \
    "python-dotenv>=1.0.1,<2.0.0" \
    "pypdf>=6.1.1,<7.0.0" \
    "rsa==4.9.1"

# 3) Copy your app code
COPY . /app

# 4) (Optional) create and switch to non-root AFTER installs
RUN useradd -m appuser
USER appuser

EXPOSE 8002
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:8002/',timeout=2).read() or sys.exit(1)"

# Adjust module if needed (main:app is docker compose common for FastAPI)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
