# Dockerfile per FinConnect Backend
FROM python:3.12-slim

# Imposta directory di lavoro
WORKDIR /app

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'applicazione
COPY . .

# Rende eseguibile lo script di avvio
RUN chmod +x entrypoint.sh

# Espone la porta
EXPOSE 8000

# Comando di avvio (migrazioni + seed + server)
ENTRYPOINT ["./entrypoint.sh"]
