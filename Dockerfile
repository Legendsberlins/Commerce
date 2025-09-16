# Use an official Python runtime
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files (optional if you use whitenoise)
# RUN python manage.py collectstatic --noinput

# Start command: run migrations then start Gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn commerce.wsgi:application --bind 0.0.0.0:8000"]