FROM python:3.10-slim

WORKDIR /app
COPY . /app

# Instala dependencias del sistema necesarias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      wireless-tools iproute2 && \
    rm -rf /var/lib/apt/lists/*

# Instala las dependencias Python
RUN pip install --no-cache-dir \
      scapy \
      rich \
      netifaces \
      .

# Por defecto, lanza el escáner en modo interactivo
ENTRYPOINT ["python", "-m", "scripts.run_scanner"]
CMD ["--help"]
