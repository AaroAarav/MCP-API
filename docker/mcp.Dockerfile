FROM python:3.11-slim

WORKDIR /app
COPY mcp_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp_app /app/mcp_app

ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["python", "mcp_app/server.py", "--sse"]
