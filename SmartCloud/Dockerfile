FROM python:3.11-slim

# Prevent Python from writing .pyc files to disc and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for Pillow and Python build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source code
COPY . /app/

# Create media and staticfiles directories
RUN mkdir -p /app/media /app/staticfiles

# Expose port 1010
EXPOSE 1010

# Command to run Gunicorn web server on port 1010
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:1010", "--workers", "3"]
