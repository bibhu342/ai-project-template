FROM python:3.11-slim
WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# python deps
COPY requirements.api.txt .
RUN pip install --no-cache-dir -r requirements.api.txt

# alembic + app
COPY alembic.ini .
COPY migrations ./migrations
COPY app ./app

# entrypoint
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# single CMD only
CMD ["./docker-entrypoint.sh"]
