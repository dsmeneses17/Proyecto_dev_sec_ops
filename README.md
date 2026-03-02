# Proyecto DevSecOps Restaurante

Plataforma para gestión de restaurantes con arquitectura desacoplada:

- **`ApiRestaurante`**: backend FastAPI (lógica de negocio + acceso a PostgreSQL).
- **`AppRestaurante`**: frontend FastAPI con templates Jinja2 (UI web + integración con backend).
- **`postgres_db`**: base de datos PostgreSQL.

---

## Requisitos previos

### Docker

- Docker Desktop 4.x+
- Docker Compose v2 (comando `docker compose`)

---

## Setup con Docker

Desde la raíz del proyecto (`Proyecto_dev_sec_ops`):

```bash
docker compose --env-file .env up --build -d
```

Esto levanta:

- `postgres_db` → `localhost:5432`
- `backend_api` (`ApiRestaurante`) → servicio interno Docker
- `frontend_api` (`AppRestaurante`) → servicio interno Docker
- `secure_gateway` (Nginx + TLS) → `https://localhost`

### 1) Inicializar tablas

> El backend no aplica migraciones automáticas al iniciar; por eso se ejecuta el script de creación de tablas.

```bash
docker compose --env-file .env exec backend_api python -m app.z_crearTablas.crearTablas
```

### 1.1) Validar base de datos

```bash
docker compose --env-file .env exec -T postgres_db psql -U <POSTGRES_USER> -d <POSTGRES_DB> -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"
```

Si retorna un número mayor a `0`, la DB está inicializada.

### 2) Verificar servicios

```bash
docker compose --env-file .env ps
```

### 3) Accesos

- App web (HTTPS): https://localhost
- API backend por gateway TLS (root): https://localhost/backend-api/
- Swagger backend por gateway TLS: https://localhost/backend-api/docs

> Nota: el gateway genera un certificado autofirmado automáticamente si no encuentra uno montado. En navegador puede aparecer advertencia de confianza en entorno local.

### 4) Ver logs

```bash
docker compose --env-file .env logs -f backend_api
docker compose --env-file .env logs -f frontend_api
docker compose --env-file .env logs -f postgres_db
```

### 5) Apagar entorno

```bash
docker compose --env-file .env down
```

Para borrar volumen de BD también:

```bash
docker compose --env-file .env down -v
```

---

## Variables de entorno

La configuración se toma desde variables de entorno (recomendado: archivo `.env` local). **No se incluyen credenciales por defecto** en el repositorio.

Variables obligatorias para la base de datos (usadas por `postgres_db` y `ApiRestaurante`):

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `DATABASE_URL` (por ejemplo: `postgresql+psycopg2://<user>:<pass>@postgres_db:5432/<db>` dentro de docker compose)

Variables obligatorias para Object Storage (S3-compatible) consumidas por `AppRestaurante`:

- `S3_BUCKET_NAME`
- `S3_REGION` (default `us-east-2`)
- `S3_ENDPOINT_URL`
- `S3_PUBLIC_BASE_URL`
- `S3_FORCE_PATH_STYLE` (`true`/`false`)
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

Variables de worker pool para procesamiento concurrente de imágenes en `AppRestaurante`:

- `IMAGE_WORKERS` (default `2`)
- `IMAGE_QUEUE_MAXSIZE` (default `100`)
- `IMAGE_QUEUE_PUT_TIMEOUT_SEC` (default `2.0`)
- `IMAGE_SHUTDOWN_TIMEOUT_SEC` (default `30`)
- `IMAGE_MAX_FILE_MB` (default `5`)
- `IMAGE_ALLOWED_CONTENT_TYPES` (default `image/jpeg,image/png,image/webp`)
- `IMAGE_ALLOWED_TARGETS` (default `logo,dish,general`)

Puedes definirlas en un archivo `.env` en la raíz (junto a `docker-compose.yml`).

Ejemplo:

```env
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
DATABASE_URL=postgresql+psycopg2://<user>:<pass>@postgres_db:5432/<db>

S3_BUCKET_NAME=mi-bucket
S3_REGION=us-east-1
S3_ENDPOINT_URL=
S3_PUBLIC_BASE_URL=
S3_FORCE_PATH_STYLE=false
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

IMAGE_WORKERS=2
IMAGE_QUEUE_MAXSIZE=100
IMAGE_QUEUE_PUT_TIMEOUT_SEC=2.0
IMAGE_SHUTDOWN_TIMEOUT_SEC=30
IMAGE_MAX_FILE_MB=5
IMAGE_ALLOWED_CONTENT_TYPES=image/jpeg,image/png,image/webp
IMAGE_ALLOWED_TARGETS=logo,dish,general
```

Nota operativa para MVP: al usar cola en memoria, ejecutar `AppRestaurante` con un solo proceso de aplicación (por ejemplo, `uvicorn` sin `--workers` o `--workers 1`) para mantener una única cola compartida.
---

## Pruebas

## Backend tests

Requiere BD de pruebas accesible y variable `DATABASE_URL`.

PowerShell (ejemplo):

```powershell
cd ApiRestaurante
$env:DATABASE_URL = "postgresql+psycopg2://<user>:<pass>@localhost:5432/<db_name>"
pytest
```

Puedes definir `DATABASE_URL` (y variables Postgres para `docker-compose`) en un archivo `.env` en la raíz (junto a `docker-compose.yml`).

## Frontend tests

```bash
cd AppRestaurante
pytest
```

---

## Carga de respaldo SQL

Si quieres importar `backup_complete.sql` dentro del PostgreSQL del compose:

```powershell
Get-Content .\backup_complete.sql | docker compose --env-file .env exec -T postgres_db psql -U <POSTGRES_USER> -d <POSTGRES_DB>
```

Si quieres restaurar desde `backup_complete.dump`:

```powershell
docker compose --env-file .env exec -T postgres_db pg_restore -U <POSTGRES_USER> -d <POSTGRES_DB> --clean --if-exists /dev/stdin < .\backup_complete.dump
```

## Backup de la base de datos

```powershell
# Backup SQL
docker compose --env-file .env exec -T postgres_db pg_dump -U <POSTGRES_USER> -d <POSTGRES_DB> > .\backup_$(Get-Date -Format "yyyyMMdd_HHmmss").sql

# Backup formato dump
docker compose --env-file .env exec -T postgres_db pg_dump -U <POSTGRES_USER> -d <POSTGRES_DB> -Fc > .\backup_$(Get-Date -Format "yyyyMMdd_HHmmss").dump
```

---

## Estructura del proyecto

```text
Proyecto_dev_sec_ops/
├─ docker-compose.yml
├─ ApiRestaurante/
│  ├─ app/
│  │  ├─ routers/
│  │  ├─ services/
│  │  ├─ repositories/
│  │  ├─ models/
│  │  ├─ schemas/
│  │  ├─ core/
│  │  ├─ utils/
│  │  └─ z_crearTablas/
│  └─ tests/
└─ AppRestaurante/
   ├─ app/
   │  ├─ routers/
   │  ├─ services/
   │  ├─ core/
   │  ├─ templates/
   │  ├─ static/
   │  └─ ui/
   └─ tests/
```

---

## Comandos útiles

```bash
# Rebuild completo
docker compose --env-file .env down -v
docker compose --env-file .env up --build -d

# Estado de servicios
docker compose --env-file .env ps

# Reiniciar solo backend
docker compose --env-file .env restart backend_api
```

---

## Documentación adicional

- Guía de deployment completa: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- Documentación de base de datos: [docs/DATABASE.md](docs/DATABASE.md)
