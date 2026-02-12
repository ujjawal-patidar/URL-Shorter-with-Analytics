FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y libpq5 curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code (GeoIP DB will be mounted)
COPY ./app ./app
COPY ./alembic ./alembic
COPY ./alembic.ini .