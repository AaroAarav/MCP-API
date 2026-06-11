FROM python:3.11-slim

WORKDIR /app
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api /app/api

ENV PYTHONPATH=/app
CMD ["uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
