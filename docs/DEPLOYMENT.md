# Instructivo de Deployment 

Este documento describe el despliegue local/servidor del proyecto con Docker Compose, incluyendo HTTPS, inicialización de base de datos y validación final.

## 1) Prerrequisitos

- Docker Desktop 4.x+ (o Docker Engine + Compose v2)
- Git
- Puertos libres: `80`, `443`, `5432`

## 2) Clonar y entrar al proyecto

```bash
git clone <URL_DEL_REPO>
cd Proyecto_dev_sec_ops
```

## 3) Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto (junto a `docker-compose.yml`):

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_password_segura
POSTGRES_DB=Restaurante
DATABASE_URL=postgresql+psycopg2://postgres:tu_password_segura@postgres_db:5432/Restaurante

# Opcional S3
S3_BUCKET_NAME=
S3_REGION=us-east-1
S3_ENDPOINT_URL=
S3_PUBLIC_BASE_URL=
S3_FORCE_PATH_STYLE=false
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# Seguridad HTTPS/sesión
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_SAMESITE=lax
ENFORCE_HTTPS_REDIRECT=true
TLS_CERT_CN=localhost
TLS_CERT_DAYS=365
```

## 4) Levantar servicios

```bash
docker compose --env-file .env up -d --build
```

Servicios esperados:

- `postgres_db`
- `backend_api`
- `frontend_api`
- `secure_gateway`

## 5) Inicializar estructura de base de datos

```bash
docker compose --env-file .env exec backend_api python -m app.z_crearTablas.crearTablas
```

## 6) (Opcional) Restaurar datos iniciales

### SQL

```bash
docker compose --env-file .env exec -T postgres_db psql -U $POSTGRES_USER -d $POSTGRES_DB < backup_complete.sql
```

### Dump binario

```bash
docker compose --env-file .env exec -T postgres_db pg_restore -U $POSTGRES_USER -d $POSTGRES_DB --clean --if-exists /dev/stdin < backup_complete.dump
```

## 7) Validar despliegue

### Estado de contenedores

```bash
docker compose --env-file .env ps
```

### Verificar HTTP -> HTTPS

```bash
curl -I http://localhost
```

Debe responder `301` hacia `https://localhost`.

### Verificar app HTTPS

```bash
curl -k https://localhost/ -o /dev/null -s -w "%{http_code}\n"
```

Debe responder `200`.

## 8) URLs de operación

- App web: `https://localhost`
- Swagger backend: `https://localhost/backend-api/docs`
- API root backend: `https://localhost/backend-api/`

> Nota: en local se usa certificado autofirmado; el navegador puede mostrar advertencia de confianza.

## 9) Operación diaria

### Logs

```bash
docker compose --env-file .env logs -f secure_gateway
docker compose --env-file .env logs -f frontend_api
docker compose --env-file .env logs -f backend_api
```

### Reinicios

```bash
docker compose --env-file .env restart
docker compose --env-file .env restart secure_gateway
```

### Apagado

```bash
docker compose --env-file .env down
```

### Apagado limpio (borra volumen de BD)

```bash
docker compose --env-file .env down -v
```

## 10) Troubleshooting rápido

### No abre `https://localhost`

1. Revisar `docker compose ps`
2. Revisar `secure_gateway`:

```bash
docker compose logs --tail=100 secure_gateway
```

3. Si el gateway cae por script de arranque, reconstruir:

```bash
docker compose up -d --build secure_gateway
```

### Error de conexión a base de datos

- Validar `DATABASE_URL` en `.env`
- Confirmar que `postgres_db` esté `running`

### Error por puertos ocupados

- Liberar puertos `80/443/5432` o cambiar mapeos en `docker-compose.yml`

---

## 11) Checklist de aceptación

- [ ] `.env` creado y completo
- [ ] `docker compose up -d --build` exitoso
- [ ] Tablas inicializadas
- [ ] `http://localhost` redirige a HTTPS
- [ ] `https://localhost` responde 200
- [ ] `https://localhost/backend-api/docs` accesible
