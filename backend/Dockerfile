# Build from the repository ROOT so the shared knowledge assets in /data ship with the image:
#   docker build -f backend/Dockerfile -t content-engine-api .
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
COPY backend/ai ./ai
COPY data ./knowledge_data
ENV KNOWLEDGE_DATA_DIR=/app/knowledge_data
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
