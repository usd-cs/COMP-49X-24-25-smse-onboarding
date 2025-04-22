FROM python:3.12-slim
WORKDIR /usr/local/app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc netcat-openbsd && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Create media directories with proper permissions
RUN mkdir -p media/profile_images && \
    chmod -R 777 media

# Create user but don't switch to it yet
# Adding a comment to test the git push
RUN useradd -m app && \
    chown -R app:app /usr/local/app

# Switch to app user only for running the application
USER app

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
