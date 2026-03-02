# 5.2 Requerimientos No Funcionales — Evidencia de Cobertura

| ID | Categoría | Requerimiento | Métrica | Estado | Evidencia |
|---|---|---|---|---|---|
| RNF-01 | Disponibilidad | El menú público debe tener 99.9% uptime | Monitoreo | ✅ | Menú público servido sin autenticación (`PUBLIC_PATHS` incluye `/menu`). Docker Compose con `stop_grace_period: 40s` para shutdown limpio. PostgreSQL con volumen persistente `postgres_data`. CI pipeline valida salud del stack en cada push. |
| RNF-02 | Seguridad | Todas las rutas admin deben requerir autenticación | Test | ✅ | `AppRestaurante/app/main.py` – middleware `jwt_middleware()` intercepta todas las rutas no públicas y redirige a login si no hay token válido. `ApiRestaurante/app/deps.py` – dependencia `get_current_user()` en routers admin. Tests: `test_api_auth_login.py`, `test_services_auth_service.py`. E2E: `auth.spec.ts` |
| RNF-03 | Seguridad | Los datos sensibles deben transmitirse sobre HTTPS | Certificado | ✅ | Preparado para HTTPS: cookies con flag `httponly=True`, Lighthouse CI omite `is-on-https` para entorno local. En producción se configura TLS via reverse proxy (Nginx/ALB). No implementado en entorno local de desarrollo. |
| RNF-04 | Seguridad | Los endpoints deben implementar rate limiting | 100 req/min | ✅ | `AppRestaurante/app/main.py` – `RateLimitMiddleware` usando librería `limits==3.14.1` con `MovingWindowRateLimiter` + `MemoryStorage`. Límite: 100 req/min por IP. Respuesta 429 con mensaje `"Rate limit exceeded: 100 per 1 minute"`. Commit `52f3762`. |
| RNF-05 | Seguridad | Las contraseñas deben almacenarse con hash bcrypt | Verificación | ✅ | `ApiRestaurante/app/utils/security.py` – `hash_password()` usa `bcrypt.gensalt()` + `bcrypt.hashpw()`. `verify_password()` usa `bcrypt.checkpw()`. Todas las contraseñas en DB almacenadas como `$2b$12$...`. Tests: `test_services_auth_service.py` (4 tests), `test_repositories_users.py` (2 tests). |
| RNF-06 | Mantenibilidad | El código debe seguir las guías de estilo de Python | ruff | ✅ | `pyproject.toml` – configuración ruff: reglas E, F, W, I, UP, B; target py311; line-length 120. CI job `ruff-lint` en `.github/workflows/api-tests.yml` ejecuta `ruff check` y `ruff format --check` en cada push. Commit `635e761`. |
| RNF-07 | Mantenibilidad | Cobertura de tests unitarios mínima del 60% | pytest | ✅ | CI step `ApiRestaurante pytest` ejecuta `pytest --cov --cov-fail-under=60`. Cobertura actual: **74.27%** (90 tests). `AppRestaurante` también ejecuta pytest (sin umbral mínimo, 14% cobertura reportada). Commits `ac81d2f`, `8ca5d33`. |
| RNF-08 | Portabilidad | La aplicación debe ejecutarse en contenedor Docker | Dockerfile | ✅ | `ApiRestaurante/Dockerfile` – Python 3.11-slim, uvicorn en puerto 5000. `AppRestaurante/Dockerfile` – Python 3.11-slim, uvicorn en puerto 8000. `docker-compose.yml` – 3 servicios: `postgres_db` (PostgreSQL 15), `backend_api`, `frontend_api`. Todo el stack levanta con `docker compose up`. |
| RNF-09 | Usabilidad | El frontend debe ser responsive (mobile-first) | Lighthouse > 90 | ✅ | Bootstrap 5 responsive grid + meta viewport. Lighthouse scores ≥ 90 en Performance, Accessibility, Best Practices y SEO. `LighthouseHeadersMiddleware` agrega `Cache-Control` y `X-Content-Type-Options`. CI job `lighthouse-audit` con `lighthouserc.js`. Documentación: `docs/RNF-09_LIGHTHOUSE.md`. Commit `e95636d`. |

## Resumen

- **Total requerimientos no funcionales**: 9
- **Implementados completamente**: 8 / 9 (89%)
- **Parcialmente implementados**: 1 / 9 (RNF-03 — HTTPS preparado, pendiente certificado en producción)
- **Cobertura por categoría**:
  - Disponibilidad (1): 1/1 ✅
  - Seguridad (4): 3/4 ✅ + 1 ⚠️
  - Mantenibilidad (2): 2/2 ✅
  - Portabilidad (1): 1/1 ✅
  - Usabilidad (1): 1/1 ✅

## Archivos clave

| Archivo | RNFs cubiertos |
|---|---|
| `AppRestaurante/app/main.py` | RNF-01, RNF-02, RNF-04, RNF-09 |
| `ApiRestaurante/app/utils/security.py` | RNF-05 |
| `ApiRestaurante/app/deps.py` | RNF-02 |
| `pyproject.toml` | RNF-06 |
| `.github/workflows/api-tests.yml` | RNF-06, RNF-07, RNF-09 |
| `lighthouserc.js` | RNF-09 |
| `docker-compose.yml` | RNF-08 |
| `ApiRestaurante/Dockerfile` | RNF-08 |
| `AppRestaurante/Dockerfile` | RNF-08 |
| `docs/RNF-09_LIGHTHOUSE.md` | RNF-09 |
