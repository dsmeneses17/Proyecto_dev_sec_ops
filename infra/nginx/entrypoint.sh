#!/bin/sh
set -eu

CERT_DIR="/etc/nginx/certs"
CERT_FILE="$CERT_DIR/tls.crt"
KEY_FILE="$CERT_DIR/tls.key"

mkdir -p "$CERT_DIR"

if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
  CERT_CN="${TLS_CERT_CN:-localhost}"
  CERT_DAYS="${TLS_CERT_DAYS:-365}"

  openssl req -x509 -nodes -newkey rsa:2048 \
    -days "$CERT_DAYS" \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -subj "/CN=$CERT_CN" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1,IP:::1"
fi

exec nginx -g 'daemon off;'
