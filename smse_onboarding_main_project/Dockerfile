FROM python:3.12-slim
WORKDIR /usr/local/app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc netcat-openbsd && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN useradd app
USER app

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
