# Use an official Python runtime as a parent image
FROM python:3.14-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create a script to run migrations and start the server
RUN echo '#!/bin/bash \n\
python manage.py migrate --noinput \n\
python manage.py collectstatic --noinput \n\
gunicorn ECOMMERCE.wsgi:application --bind 0.0.0.0:$PORT' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Expose the port
EXPOSE 8000

# Run the application
CMD ["/app/entrypoint.sh"]
