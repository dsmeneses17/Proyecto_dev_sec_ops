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
docker compose up --build -d
```

Esto levanta:

- `postgres_db` → `localhost:5432`
- `backend_api` (`ApiRestaurante`) → `localhost:5001`
- `frontend_api` (`AppRestaurante`) → `localhost:8000`

### 1) Inicializar tablas

> El backend no aplica migraciones automáticas al iniciar; por eso se ejecuta el script de creación de tablas.

```bash
docker compose exec backend_api python -m app.z_crearTablas.crearTablas
```

### 2) Verificar servicios

```bash
docker compose ps
```

### 3) Accesos

- App web: http://localhost:8000
- API backend (root): http://localhost:5001/
- Swagger backend: http://localhost:5001/docs

### 4) Ver logs

```bash
docker compose logs -f backend_api
docker compose logs -f frontend_api
docker compose logs -f postgres_db
```

### 5) Apagar entorno

```bash
docker compose down
```

Para borrar volumen de BD también:

```bash
docker compose down -v
```

---

## Variables de entorno

`docker-compose.yml` ya define valores base para backend y base de datos.

Variables obligatorias para Object Storage (S3-compatible) consumidas por `AppRestaurante`:

- `S3_BUCKET_NAME`
- `S3_REGION` (default `us-east-2`)
- `S3_ENDPOINT_URL`
- `S3_PUBLIC_BASE_URL`
- `S3_FORCE_PATH_STYLE` (`true`/`false`)
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

Puedes definirlas en un archivo `.env` en la raíz (junto a `docker-compose.yml`).

Ejemplo:

```env
S3_BUCKET_NAME=mi-bucket
S3_REGION=us-east-1
S3_ENDPOINT_URL=
S3_PUBLIC_BASE_URL=
S3_FORCE_PATH_STYLE=false
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
```
---

## Pruebas

## Backend tests

Requiere BD de pruebas accesible y variable `DATABASE_URL` apuntando a `Restaurante_test`.

PowerShell (ejemplo):

```powershell
cd ApiRestaurante
$env:DATABASE_URL = "postgresql+psycopg2://postgres:1234@localhost:5432/Restaurante_test"
pytest
```

## Frontend tests

```bash
cd AppRestaurante
pytest
```

---

## Carga de respaldo SQL

Si quieres importar `backup_complete.sql` dentro del PostgreSQL del compose:

```powershell
Get-Content .\backup_complete.sql | docker compose exec -T postgres_db psql -U postgres -d Restaurante
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
docker compose down -v
docker compose up --build -d

# Estado de servicios
docker compose ps

# Reiniciar solo backend
docker compose restart backend_api
```
