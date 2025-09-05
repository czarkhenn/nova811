FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        gettext \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ./backend/requirements/ requirements/
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements/local.txt

# Copy project
COPY ./backend /app/
