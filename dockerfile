# Grundlegendes Python-Image verwenden
FROM python:3.12-slim

# Installiere erforderliche Bibliotheken
RUN apt-get update && apt-get install -y libpq-dev build-essential

# Arbeitsverzeichnis im Container erstellen und festlegen
WORKDIR /app

# Anforderungen (falls vorhanden) ins Image kopieren und installieren
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere Python-Dateien und das wait-for-it Skript
COPY *.py /app/

CMD ["sh", "-c", "python -u migrate.py && python -u read.py && python -u update.py && python -u delete.py"]