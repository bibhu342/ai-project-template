FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.api.txt .
RUN pip install --no-cache-dir -r requirements.api.txt

# ⬇️ ADD THESE
COPY alembic.ini .
COPY migrations ./migrations

COPY app ./app

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# optional: we’ll switch to entrypoint in Step 3
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh
CMD ["./docker-entrypoint.sh"]
