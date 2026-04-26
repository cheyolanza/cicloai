FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    STORAGE_DIR=/app/data

WORKDIR /app

RUN useradd --create-home --shell /usr/sbin/nologin cicloai

COPY --from=builder /opt/venv /opt/venv
COPY src ./src
COPY data ./data
COPY assets ./assets
COPY alembic ./alembic
COPY alembic.ini .

RUN mkdir -p /app/storage/vector_store /app/assets/payments \
    && chown -R cicloai:cicloai /app/data /app/storage /app/assets/payments

USER cicloai
ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()"

CMD ["uvicorn", "cicloai.interfaces.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
