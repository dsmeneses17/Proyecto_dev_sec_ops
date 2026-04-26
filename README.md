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

## Docs entrega 2
- [Documentacion principal](docs/DOCUMENTACION_PROYECTO.md)
- [Estrategia de Seguridad](https://github.com/dsmeneses17/Proyecto_dev_sec_ops/blob/main/docs/Seguridad/ESTRATEGIA_SEGURIDAD.md)
- [Reporte vulnerabilidades Backend](https://github.com/dsmeneses17/Proyecto_dev_sec_ops/blob/main/docs/Seguridad/Report%20Vulneravilidades%20-%20livemenu-foundation-dev-backend.pdf)
- [Reporte vulnerabilidades Frontend](https://github.com/dsmeneses17/Proyecto_dev_sec_ops/blob/main/docs/Seguridad/Reporte%20Vulnerabilidades%20-%20livemenu-foundation-dev-frontend.pdf)
- [Arquitectura GCP](https://github.com/dsmeneses17/Proyecto_dev_sec_ops/blob/main/docs/ARQUITECTURA_GCP_ENTREGA2.md)
- [Arquitectura GCP PNG](https://github.com/dsmeneses17/Proyecto_dev_sec_ops/blob/main/docs/arquitectura_gcp_actual.png)

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
| `TF_VAR_DB_PASSWORD` | Opcional/legado: override de password Cloud SQL. Por defecto Terraform toma `db-password` desde Secret Manager. |
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

### Terraform local (secretos)

- Mantener variables no sensibles en `infra/terraform/envs/foundation-dev/terraform.auto.tfvars`.
- Mantener secretos locales fuera de git en `infra/terraform/envs/foundation-dev/terraform.local.tfvars`.
- Usar como plantilla `infra/terraform/envs/foundation-dev/terraform.secrets.example.tfvars`.
- `infra/terraform/.gitignore` ignora `terraform.local.tfvars`, `terraform.tfvars` y `*.secrets.tfvars`.
- Para plan local alineado con CI, exportar secretos por entorno o usar `-var-file=terraform.local.tfvars` de forma explicita.

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

- `drift-check-dev`: ejecuta `terraform plan -refresh-only -detailed-exitcode` antes del plan normal, genera reporte de drift y publica artefacto `terraform-dev-drift-report`.
- `manual-approval-drift-dev`: en `push` a `main`, solicita aprobacion manual si se detecta drift accionable antes de continuar.
- `plan-dev`: init, validate y plan de Terraform para foundation-dev.
- `security-scan-dev`: escaneo IaC con Trivy y bloqueo por severidad HIGH/CRITICAL.
- `validate-plan-dev`: valida el plan y bloquea cambios destructivos.
- `manual-approval-dev`: requiere aprobacion manual explicita antes de aplicar.
- `apply-dev`: aplica Terraform en push a main solo si plan, escaneo, validacion y aprobacion manual fueron exitosos.

Reglas de drift:

- Si hay drift accionable en PR o en ejecuciones que no son `push` a `main`, el pipeline falla para forzar investigacion.
- Si hay drift accionable en `push` a `main`, se exige aprobacion manual adicional (`manual-approval-drift-dev`) antes del plan/apply.
- El reporte conserva drift informativo (metadata de proveedor/runtime) para observabilidad, pero no bloquea por si solo.
- Se ignora de forma explicita `google_storage_bucket_object.rotate_secret_source` en el conteo de drift accionable por ser artefacto efimero de empaquetado de Cloud Function.
- En `push` a `main`, si solo existe drift informativo (por ejemplo versiones rotadas de secretos), el pipeline ejecuta `terraform apply -refresh-only` para reconciliar estado sin cambiar infraestructura remota.

### Habilitar auditoria de objetos en Cloud Storage (Data Access)

Para identificar quien borra/crea objetos (por ejemplo `rotate_secret_source`) se deben habilitar Data Access logs para Cloud Storage.

```bash
PROJECT_ID="proyecto-devsecops-493813"

gcloud projects get-iam-policy "$PROJECT_ID" --format=json > /tmp/project-iam-policy.json

jq '
  .auditConfigs = (
    ((.auditConfigs // []) | map(select(.service != "storage.googleapis.com")))
    + [{
      service: "storage.googleapis.com",
      auditLogConfigs: [
        {logType: "DATA_READ"},
        {logType: "DATA_WRITE"}
      ]
    }]
  )
' /tmp/project-iam-policy.json > /tmp/project-iam-policy.with-storage-audit.json

gcloud projects set-iam-policy "$PROJECT_ID" /tmp/project-iam-policy.with-storage-audit.json
```

El flujo anterior preserva los bindings existentes al partir de la policy actual del proyecto.

Consulta recomendada para rastrear actor de drift en bucket de imagenes:

```bash
gcloud logging read \
  'protoPayload.serviceName="storage.googleapis.com" AND resource.labels.bucket_name="livemenu-foundation-dev-images-proyecto-devsecops-493813" AND (protoPayload.methodName:"storage.objects.delete" OR protoPayload.methodName:"storage.objects.create" OR protoPayload.methodName:"storage.objects.update")' \
  --project "$PROJECT_ID" \
  --freshness=30d \
  --limit=200 \
  --format='table(timestamp,protoPayload.methodName,protoPayload.authenticationInfo.principalEmail,protoPayload.requestMetadata.callerSuppliedUserAgent,protoPayload.resourceName)'
```

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
