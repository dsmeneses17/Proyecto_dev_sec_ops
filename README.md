# Proyecto DevSecOps - Restaurante Digital

Plataforma de menu digital para restaurantes con frontend web, API REST y despliegue local con Docker Compose. El proyecto tambien incluye arquitectura objetivo en GCP con Terraform.

## Acceso rapido a documentacion

- [Documentacion principal](docs/DOCUMENTACION_PROYECTO.md)
- [Mapa de arquitectura](docs/MAPA_ARQUITECTURA.md)
- [Diagrama GCP en PNG](docs/arquitectura_gcp_actual.png)
- [Deployment local](docs/DEPLOYMENT.md)
- [API](docs/API_DOCUMENTATION.md)
- [Cobertura requerimientos](docs/COBERTURA_REQUERIMIENTOS.md)
- [Cobertura RNF](docs/COBERTURA_RNF.md)
- [Testing](docs/TESTING.md)

## Estado actual del proyecto

### Local (operacion diaria)

| Servicio | Tecnologia | Rol |
|----------|------------|-----|
| `frontend_api` | FastAPI + Jinja2 + Bootstrap | Interfaz web |
| `backend_api` | FastAPI + SQLAlchemy + Pydantic | API REST |
| `postgres_db` | PostgreSQL 15 | Persistencia |
| `secure_gateway` | Nginx + TLS | Entrada HTTPS y enrutamiento |

### GCP (estado Terraform)

Estado actual en `infra/terraform/envs/foundation-dev/terraform.auto.tfvars`:

- `create_cloud_dns=false`
- `create_frontend_lb=false`
- `create_waf_policy=true`

Esto significa que la base de red y seguridad esta activa por Terraform, pero no todo el flujo publico de frontend/LB esta habilitado en ese entorno base.

## Arquitectura local

```text
Internet / Navegador
       |
       v
secure_gateway (80/443)
  |- /backend-api/* -> backend_api:5000
  |- /*             -> frontend_api:8000
backend_api -> postgres_db:5432
frontend_api -> backend_api
```

## Arquitectura en la nube (GCP)

Arquitectura referencial/objetivo en GCP:

```text
Usuarios
  |
  v
Global HTTPS Load Balancer
  |
  v
Cloud Armor (WAF)
  |
  v
Serverless NEG
  |
  v
Cloud Run frontend -> Cloud Run backend
                |\
                | -> Cloud SQL PostgreSQL
                | -> Secret Manager
                | -> Cloud Storage
```

Referencias detalladas:

- [Mapa de arquitectura GCP](docs/MAPA_ARQUITECTURA.md)
- [Diagrama GCP en PNG](docs/arquitectura_gcp_actual.png)
- [Documento tecnico consolidado](docs/DOCUMENTACION_PROYECTO.md)

## Inicio rapido local

### 1. Crear `.env`

Usa [.env.example](.env.example) y define minimo:

```env
POSTGRES_USER=mi_usuario
POSTGRES_PASSWORD=mi_password_segura
POSTGRES_DB=Restaurante
DATABASE_URL=postgresql+psycopg2://mi_usuario:mi_password_segura@postgres_db:5432/Restaurante
SECRET_KEY=una_clave_larga_y_segura
```

### 2. Levantar servicios

```bash
docker compose --env-file .env up -d --build
```

### 3. Crear tablas

```bash
docker compose --env-file .env exec backend_api python -m app.z_crearTablas.crearTablas
```

### 4. Validar endpoints

- `https://localhost`
- `https://localhost/backend-api/docs`
- `https://localhost/backend-api/`

## Controles de seguridad implementados

- HTTPS con redireccion HTTP -> HTTPS en gateway.
- JWT para autenticacion/autorizacion.
- `SECRET_KEY` requerida por frontend y backend.
- Rate limit de 100 solicitudes por minuto por IP.
- Cookies de sesion seguras (`SESSION_COOKIE_SECURE`, `SESSION_COOKIE_SAMESITE`).
- Uso de Secret Manager en arquitectura GCP.

## Variables de entorno clave

### GitHub Secrets

| Variable | Uso |
|----------|-----|
| `GCP_DEPLOY_SA` | Service Account usada por GitHub Actions para despliegue en GCP (OIDC). |
| `GCP_WIF_PROVIDER` | Workload Identity Provider para federacion OIDC GitHub -> GCP. |
| `POSTGRES_USER` | Usuario PostgreSQL para despliegue local/compose. |
| `POSTGRES_PASSWORD` | Password PostgreSQL para despliegue local/compose. |
| `POSTGRES_DB` | Nombre de base de datos PostgreSQL para despliegue local/compose. |
| `TF_VAR_DB_PASSWORD` | Password de Cloud SQL inyectada a Terraform como variable sensible. |
| `TF_VAR_JWT_SECRET` | Secreto JWT inyectado a Terraform como variable sensible. |

### GitHub Variables (Repository/Environment Variables)

| Variable | Uso |
|----------|-----|
| `ARTIFACT_REGISTRY_REPO` | Repositorio de imagenes para frontend/backend en pipeline. |
| `CLOUD_RUN_BACKEND_SERVICE` | Nombre del servicio backend en Cloud Run. |
| `CLOUD_RUN_FRONTEND_SERVICE` | Nombre del servicio frontend en Cloud Run. |
| `GCP_PROJECT_ID` | Proyecto de GCP objetivo para infraestructura y despliegue. |
| `GCP_REGION` | Region principal para recursos (Cloud Run, Artifact Registry, etc.). |
| `TF_STATE_BUCKET` | Bucket remoto del estado Terraform. |
| `TF_STATE_PREFIX_DEV` | Prefijo de estado para entorno dev/foundation-dev. |
| `TF_VAR_SUBNETS` | Mapa de subredes consumido por Terraform (`var.subnets`). |

### Variables de aplicacion (runtime)

| Variable | Uso |
|----------|-----|
| `DATABASE_URL` | Conexion a PostgreSQL en backend. |
| `SECRET_KEY` | Firma y validacion JWT en frontend y backend. |
| `BACKEND_URL` | URL backend usada por frontend. |
| `SESSION_COOKIE_SECURE` | Cookie solo por HTTPS. |
| `SESSION_COOKIE_SAMESITE` | Politica SameSite. |
| `ENFORCE_HTTPS_REDIRECT` | Forzar HTTPS en frontend. |
| `S3_*` / `AWS_*` | Object storage compatible S3. |
| `GCS_*` | Object storage en GCP. |
| `IMAGE_*` | Configuracion del worker de imagenes. |

## Pruebas y calidad

### Backend

```bash
cd ApiRestaurante
pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=60
```

### Frontend

```bash
cd AppRestaurante
pytest tests/ --cov=app --cov-report=term-missing
```

### E2E

```bash
cd e2e
npm ci
npx playwright install --with-deps
E2E_BASE_URL=https://localhost npm run test:ci
```

### Lint

```bash
ruff check --config pyproject.toml
ruff format --check --config pyproject.toml
```

## CI/CD

Workflows configurados en GitHub Actions:

- [api-tests.yml](.github/workflows/api-tests.yml) para calidad y pruebas de aplicacion.
- [terraform-infra.yml](.github/workflows/terraform-infra.yml) para infraestructura IaC en foundation-dev.

### Workflow aplicacion

Archivo: [api-tests.yml](.github/workflows/api-tests.yml)

- `ruff-lint`
- `apirestaurante-pytest`
- `apprestaurante-pytest`
- `playwright-e2e`
- `lighthouse-audit`

### Workflow infraestructura (Terraform)

Archivo: [terraform-infra.yml](.github/workflows/terraform-infra.yml)

- `plan-dev`: init, validate y plan de Terraform para foundation-dev.
- `security-scan-dev`: escaneo IaC con Trivy y bloqueo por severidad HIGH/CRITICAL.
- `apply-dev`: aplica Terraform en push a main, condicionado a plan y escaneo exitosos.

## Backup y restauracion

### Importar SQL

```bash
docker compose --env-file .env exec -T postgres_db psql -U $POSTGRES_USER -d $POSTGRES_DB < backup_complete.sql
```

### Importar dump binario

```bash
docker compose --env-file .env exec -T postgres_db pg_restore -U $POSTGRES_USER -d $POSTGRES_DB --clean --if-exists /dev/stdin < backup_complete.dump
```

## Operacion diaria

```bash
docker compose --env-file .env ps
docker compose --env-file .env logs -f secure_gateway
docker compose --env-file .env logs -f frontend_api
docker compose --env-file .env logs -f backend_api
docker compose --env-file .env restart
docker compose --env-file .env down
```
