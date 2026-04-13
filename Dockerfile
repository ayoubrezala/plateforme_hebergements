FROM python:3.11-slim

# Dépendances système pour le connecteur MariaDB
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libmariadb-dev gcc && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5050

CMD ["python", "serveur.py"]
