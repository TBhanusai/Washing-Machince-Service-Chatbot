# Dockerfile
FROM python:3.10-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY ingest.py chatbot.py app.py ./
COPY data ./data
COPY faiss_index ./faiss_index

EXPOSE 8501

CMD ["sh", "-c", "\
  if [ ! -d ./faiss_index ] || [ -z \"$(ls -A ./faiss_index)\" ]; then \
    echo 'FAISS index not found — running ingest.py'; \
    python ingest.py || echo 'Ingest script failed'; \
  else \
    echo 'FAISS index exists, skipping ingest.'; \
  fi && \
  streamlit run app.py --server.port=8501 --server.address=0.0.0.0 \
"]



