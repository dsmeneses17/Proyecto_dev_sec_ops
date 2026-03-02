# 🍽️ Proyecto DevSecOps — Restaurante Digital

Plataforma de menú digital para restaurantes con arquitectura desacoplada, seguridad TLS y pipeline CI/CD completo.

| Servicio | Tecnología | Rol |
|----------|-----------|-----|
| **`backend_api`** (ApiRestaurante) | FastAPI · SQLAlchemy · Pydantic v2 | API REST (lógica de negocio + PostgreSQL) |
| **`frontend_api`** (AppRestaurante) | FastAPI · Jinja2 · Bootstrap 5 | Interfaz web (UI + integración con backend) |
| **`postgres_db`** | PostgreSQL 15 | Base de datos relacional |
| **`secure_gateway`** | Nginx + TLS autofirmado | Reverse proxy HTTPS, terminación SSL |

---

## Arquitectura

```text
 Internet / Navegador
        │
        ▼
 ┌──────────────┐
 │ secure_gateway│  ← Nginx (puerto 443/80)
 │   TLS term.   │
 └──┬────────┬──┘
     │        │
     │  /backend-api/*    → backend_api:5000
     │  /*                → frontend_api:8000
     │
 ┌───▼───┐  ┌───▼────┐
 │frontend│  │ backend │
 │  :8000 │  │  :5000  │
 └────────┘  └───┬────┘
                  │
            ┌─────▼─────┐
            │ postgres_db│
            │   :5432    │
            └────────────┘
```

---

## Requisitos previos

- **Docker Desktop** 4.x+ con Docker Compose v2
- (Opcional) Python 3.11+ y Node.js 20+ para desarrollo local

---

## Inicio rápido

### 1) Configurar variables de entorno

Crear un archivo `.env` en la raíz (junto a `docker-compose.yml`). Ver [`.env.example`](.env.example) como referencia.

Variables **obligatorias**:

```env
POSTGRES_USER=mi_usuario
POSTGRES_PASSWORD=mi_contraseña
POSTGRES_DB=Restaurante
DATABASE_URL=postgresql+psycopg2://mi_usuario:mi_contraseña@postgres_db:5432/Restaurante
```

### 2) Levantar el entorno

```bash
docker compose --env-file .env up --build -d
```

### 3) Inicializar tablas

> El backend no aplica migraciones automáticas; se ejecuta el script de creación de tablas.

```bash
docker compose --env-file .env exec backend_api python -m app.z_crearTablas.crearTablas
```

### 4) Verificar servicios

```bash
docker compose --env-file .env ps
```

Los 4 servicios deben mostrar estado `running`.

### 5) Accesos

| URL | Descripción |
|-----|-------------|
| `https://localhost` | Aplicación web (frontend) |
| `https://localhost/backend-api/docs` | Swagger UI (documentación interactiva) |
| `https://localhost/backend-api/` | API REST root |

> ⚠️ El gateway genera un certificado TLS autofirmado. En el navegador aparecerá una advertencia de confianza — es esperado en entorno local.

### 6) Ver logs

```bash
docker compose --env-file .env logs -f backend_api
docker compose --env-file .env logs -f frontend_api
docker compose --env-file .env logs -f secure_gateway
```

### 7) Apagar entorno

```bash
docker compose --env-file .env down        # preserva datos
docker compose --env-file .env down -v     # borra volumen de BD
```

---

## Variables de entorno

Todas se configuran en el archivo `.env`. **No se incluyen credenciales** en el repositorio.

### Base de datos

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `POSTGRES_USER` | ✅ | Usuario PostgreSQL |
| `POSTGRES_PASSWORD` | ✅ | Contraseña PostgreSQL |
| `POSTGRES_DB` | ✅ | Nombre de la base de datos |
| `DATABASE_URL` | ✅ | Connection string (usado por el backend) |

### Object Storage (S3-compatible)

| Variable | Default | Descripción |
|----------|---------|-------------|
| `S3_BUCKET_NAME` | — | Nombre del bucket |
| `S3_REGION` | `us-east-1` | Región AWS/S3 |
| `S3_ENDPOINT_URL` | — | Endpoint personalizado (MinIO, etc.) |
| `S3_PUBLIC_BASE_URL` | — | URL base pública para imágenes |
| `S3_FORCE_PATH_STYLE` | `false` | Path-style access |
| `AWS_ACCESS_KEY_ID` | — | Credencial de acceso |
| `AWS_SECRET_ACCESS_KEY` | — | Credencial secreta |

### Worker pool de imágenes

| Variable | Default | Descripción |
|----------|---------|-------------|
| `IMAGE_WORKERS` | `2` | Threads de procesamiento |
| `IMAGE_QUEUE_MAXSIZE` | `100` | Tamaño máximo de la cola |
| `IMAGE_QUEUE_PUT_TIMEOUT_SEC` | `2.0` | Timeout para encolar (s) |
| `IMAGE_SHUTDOWN_TIMEOUT_SEC` | `30` | Timeout de apagado (s) |
| `IMAGE_MAX_FILE_MB` | `5` | Tamaño máximo de archivo (MB) |
| `IMAGE_ALLOWED_CONTENT_TYPES` | `image/jpeg,image/png,image/webp` | MIME types permitidos |
| `IMAGE_ALLOWED_TARGETS` | `logo,dish,general` | Targets de subida |

### Seguridad / Sesión

| Variable | Default | Descripción |
|----------|---------|-------------|
| `SESSION_COOKIE_SECURE` | `true` | Cookie secure flag |
| `SESSION_COOKIE_SAMESITE` | `lax` | SameSite policy |
| `ENFORCE_HTTPS_REDIRECT` | `true` | Redirigir HTTP → HTTPS |
| `TLS_CERT_CN` | `localhost` | Common Name del certificado |
| `TLS_CERT_DAYS` | `365` | Días de validez del certificado |

---

## Pruebas

### Backend (ApiRestaurante)

Requiere PostgreSQL accesible y `DATABASE_URL` definida.

```bash
cd ApiRestaurante
export DATABASE_URL="postgresql+psycopg2://<user>:<pass>@localhost:5432/<db>"
pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=60
```

### Frontend (AppRestaurante)

```bash
cd AppRestaurante
pytest tests/ --cov=app --cov-report=term-missing
```

### E2E (Playwright)

```bash
cd e2e
npm ci
npx playwright install --with-deps
E2E_BASE_URL=https://localhost npm run test:ci
```

### Lighthouse (RNF-09)

```bash
npm install -g @lhci/cli
lhci autorun --config=lighthouserc.js
```

### Linter (Ruff — RNF-06)

```bash
ruff check --config pyproject.toml
ruff format --check --config pyproject.toml
```

---

## CI/CD

El pipeline se ejecuta en GitHub Actions en cada push a `main`. Archivo: [`.github/workflows/api-tests.yml`](.github/workflows/api-tests.yml).

| Job | Descripción | RNF |
|-----|-------------|-----|
| `ruff-lint` | Linting Python con Ruff | RNF-06 |
| `apirestaurante-pytest` | Tests del backend + cobertura ≥ 60% | RNF-07 |
| `apprestaurante-pytest` | Tests del frontend | RNF-07 |
| `playwright-e2e` | Tests end-to-end con Docker Compose | — |
| `lighthouse-audit` | Auditoría Lighthouse ≥ 90 | RNF-09 |

---

## Backup y restauración

### Importar respaldo SQL

```bash
cat backup_complete.sql | docker compose --env-file .env exec -T postgres_db psql -U $POSTGRES_USER -d $POSTGRES_DB
```

### Importar respaldo dump

```bash
docker compose --env-file .env exec -T postgres_db pg_restore \
  -U $POSTGRES_USER -d $POSTGRES_DB --clean --if-exists \
  /dev/stdin < backup_complete.dump
```

### Crear backup

```bash
# SQL
docker compose --env-file .env exec -T postgres_db \
  pg_dump -U $POSTGRES_USER -d $POSTGRES_DB > backup_$(date +%Y%m%d_%H%M%S).sql

# Dump binario
docker compose --env-file .env exec -T postgres_db \
  pg_dump -U $POSTGRES_USER -d $POSTGRES_DB -Fc > backup_$(date +%Y%m%d_%H%M%S).dump
```

---

## Estructura del proyecto

```text
Restaurante/
├── docker-compose.yml
├── pyproject.toml            # Config de Ruff (linter)
├── lighthouserc.js           # Config de Lighthouse CI
├── .env.example              # Plantilla de variables de entorno
├── .github/workflows/
│   └── api-tests.yml         # Pipeline CI (5 jobs)
├── infra/
│   └── nginx/                # Reverse proxy TLS (secure_gateway)
│       ├── Dockerfile
│       ├── nginx.conf
│       └── entrypoint.sh
├── ApiRestaurante/           # Backend (API REST)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── routers/          # Endpoints (auth, restaurants, categories, dishes, analytics, public_menu)
│   │   ├── services/         # Lógica de negocio
│   │   ├── repositories/     # Acceso a datos
│   │   ├── models/           # Modelos SQLAlchemy
│   │   ├── schemas/          # Schemas Pydantic
│   │   ├── core/             # Seguridad, config
│   │   ├── utils/            # Utilidades (cache, slug, JWT)
│   │   └── z_crearTablas/    # Script creación de tablas
│   └── tests/
├── AppRestaurante/           # Frontend (Web UI)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── routers/          # Rutas web (auth, restaurant, category, dish, menu, etc.)
│   │   ├── services/         # Llamadas al backend API
│   │   ├── templates/        # Jinja2 + Bootstrap 5
│   │   ├── static/           # CSS, imágenes
│   │   ├── ui/               # Template engine config
│   │   ├── core/             # Config, seguridad
│   │   └── utils/            # Helpers
│   └── tests/
├── e2e/                      # Tests end-to-end
│   ├── playwright.config.ts
│   └── tests/
├── docs/                     # Documentación del proyecto
│   ├── API_DOCUMENTATION.md  # 30 endpoints documentados
│   ├── COBERTURA_REQUERIMIENTOS.md  # 24/24 requerimientos funcionales
│   ├── COBERTURA_RNF.md      # Requerimientos no funcionales
│   ├── MAPA_ARQUITECTURA.md  # Diagrama Mermaid
│   ├── RNF-09_LIGHTHOUSE.md  # Evidencia Lighthouse
│   └── TESTING.md            # Estrategia de testing
└── backup_complete.sql       # Respaldo de datos iniciales
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

# Reiniciar gateway (regenera certificado si fue eliminado)
docker compose --env-file .env restart secure_gateway
```

---

## Documentación

| Documento | Descripción |
|-----------|-------------|
| [API Documentation](docs/API_DOCUMENTATION.md) | Documentación completa de los 30 endpoints |
| [Cobertura Requerimientos](docs/COBERTURA_REQUERIMIENTOS.md) | Tabla de cumplimiento de 24 requerimientos funcionales |
| [Cobertura RNF](docs/COBERTURA_RNF.md) | Cobertura de requerimientos no funcionales |
| [Mapa Arquitectura](docs/MAPA_ARQUITECTURA.md) | Diagrama de arquitectura (Mermaid) |
| [Lighthouse](docs/RNF-09_LIGHTHOUSE.md) | Evidencia de auditoría Lighthouse |
| [Testing](docs/TESTING.md) | Estrategia y plan de pruebas |
