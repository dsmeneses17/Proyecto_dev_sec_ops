FROM python:3.11-slim

WORKDIR /app

# Instala compiladores para dependencias nativas
RUN apt-get update && \
    apt-get install -y build-essential gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Exponer puerto de FastAPI
EXPOSE 5000

# Arrancar Uvicorn apuntando al módulo correcto
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
