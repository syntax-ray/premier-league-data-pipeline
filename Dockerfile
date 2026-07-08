FROM python:3.13-slim

WORKDIR /app

COPY requirements/ingestion.txt .

RUN pip install --no-cache-dir -r ingestion.txt

COPY scripts ./scripts

CMD [ "python", "scripts/pipeline.py" ]