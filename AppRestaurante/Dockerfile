FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y build-essential gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir google-cloud-storage

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
