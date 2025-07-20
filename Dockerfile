FROM python:3.12-slim

# System settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build deps and pipenv
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*
RUN pip install pipenv

# Set working directory
WORKDIR /app

# Copy pipenv files first for Docker build cache efficiency
COPY Pipfile Pipfile.lock ./

# Install deps (system-wide, no venv inside image)
RUN pipenv install --deploy --system

# Now copy the rest of the code
COPY . .

# Collect static files (optional for Django)
# RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Recommended for dev. For production, use gunicorn or uwsgi instead.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
