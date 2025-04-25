FROM python:3.12-slim
WORKDIR /usr/local/app

# Install system dependencies including SSL-related packages
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    netcat-openbsd \
    ca-certificates \
    openssl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install and configure certificates
RUN update-ca-certificates --fresh && \
    pip install --upgrade pip && \
    pip install certifi && \
    pip install pyopenssl && \
    pip install ndg-httpsclient && \
    pip install pyasn1 && \
    pip install pip-system-certs

# Set Python SSL environment variables
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV PYTHONHTTPSVERIFY=0
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Create a custom SSL configuration
RUN echo "import ssl" > /usr/local/lib/python3.12/site-packages/ssl_fix.py && \
    echo "ssl._create_default_https_context = ssl._create_unverified_context" >> /usr/local/lib/python3.12/site-packages/ssl_fix.py

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
CMD ["python", "-c", "import ssl_fix; from django.core.management import execute_from_command_line; execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])"]
