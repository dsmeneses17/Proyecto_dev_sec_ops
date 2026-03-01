# 📋 Documentación Completa de Pruebas — Proyecto Restaurante

> **Última actualización:** Febrero 2026  
> **Repositorio:** `dsmeneses17/Proyecto_dev_sec_ops`

---

## Tabla de Contenidos

1. [Visión General](#1-visión-general)
2. [Arquitectura de Pruebas](#2-arquitectura-de-pruebas)
3. [Niveles de Prueba](#3-niveles-de-prueba)
   - 3.1 [Pruebas Unitarias de Servicios (ApiRestaurante)](#31-pruebas-unitarias-de-servicios-apirestaurante)
   - 3.2 [Pruebas de Repositorios (ApiRestaurante)](#32-pruebas-de-repositorios-apirestaurante)
   - 3.3 [Pruebas de Contrato API (ApiRestaurante)](#33-pruebas-de-contrato-api-apirestaurante)
   - 3.4 [Pruebas Unitarias de Servicios (AppRestaurante)](#34-pruebas-unitarias-de-servicios-apprestaurante)
   - 3.5 [Pruebas E2E con Playwright](#35-pruebas-e2e-con-playwright)
4. [Infraestructura de Pruebas](#4-infraestructura-de-pruebas)
   - 4.1 [Fixtures y conftest.py](#41-fixtures-y-conftestpy)
   - 4.2 [Helpers de Playwright](#42-helpers-de-playwright)
   - 4.3 [Configuración de Playwright](#43-configuración-de-playwright)
5. [Integración Continua (CI)](#5-integración-continua-ci)
   - 5.1 [Workflow: api-tests.yml](#51-workflow-api-testsyml)
   - 5.2 [Jobs del Pipeline](#52-jobs-del-pipeline)
   - 5.3 [Gestión de Secretos](#53-gestión-de-secretos)
6. [Ejecución Local](#6-ejecución-local)
7. [Matriz de Cobertura](#7-matriz-de-cobertura)
8. [Resumen de Casos de Prueba](#8-resumen-de-casos-de-prueba)
9. [Resultados CI — Última Ejecución Exitosa](#9-resultados-ci--última-ejecución-exitosa)

---

## 1. Visión General

El proyecto implementa una estrategia de pruebas en **tres niveles** (pirámide de testing):

```
         ┌──────────────┐
         │   E2E (7)    │  ← Playwright (navegador real)
         ├──────────────┤
         │Contrato (14) │  ← FastAPI TestClient (in-process)
         ├──────────────┤
         │  Repos (9)   │  ← Postgres real vía SQLAlchemy
         ├──────────────┤
         │Servicios (27)│  ← Mocks puros (unittest.mock)
         └──────────────┘
              Base
```

| Nivel | Framework | BD necesaria | Velocidad | Cantidad |
|---|---|---|---|---|
| Unitario — Servicios (ApiRestaurante) | pytest + `monkeypatch` | ❌ No | ⚡ Muy rápida | 10 tests |
| Unitario — Servicios (AppRestaurante) | pytest + `monkeypatch` | ❌ No | ⚡ Muy rápida | 17 tests |
| Repositorios | pytest + SQLAlchemy | ✅ Postgres | 🔄 Media | 9 tests |
| Contrato API | pytest + FastAPI `TestClient` | ✅ Postgres | 🔄 Media | 14 tests |
| E2E | Playwright (TypeScript) | ✅ Docker Compose completo | 🐢 Lenta | 7 tests |
| **Total** | | | | **57 tests** |

---

## 2. Arquitectura de Pruebas

```
Restaurante/
├── ApiRestaurante/
│   └── tests/
│       ├── conftest.py                        # Fixtures compartidos (engine, session, factories)
│       ├── test_services_auth_service.py      # Unitarios — servicio de autenticación
│       ├── test_services_category_service.py  # Unitarios — servicio de categorías
│       ├── test_services_menu_service.py      # Unitarios — servicio de menú público
│       ├── test_services_restaurant_service.py# Unitarios — servicio de restaurantes
│       ├── test_repositories_users.py         # Repositorio — usuarios (Postgres)
│       ├── test_repositories_restaurants.py   # Repositorio — restaurantes (Postgres)
│       ├── test_repositories_categories.py    # Repositorio — categorías (Postgres)
│       ├── test_repositories_dishes.py        # Repositorio — platos (Postgres)
│       ├── test_api_auth_login.py             # Contrato API — login
│       ├── test_api_auth_register.py          # Contrato API — registro de usuarios (RF02)
│       └── test_api_contract_public_menu.py   # Contrato API — menú público
│
├── AppRestaurante/
│   └── tests/
│       ├── test_services_auth_service.py      # Unitarios — servicio auth del frontend
│       ├── test_services_categoria_service.py # Unitarios — servicio categorías del frontend
│       ├── test_services_menu_service.py      # Unitarios — servicio menú del frontend
│       └── test_services_dish_service.py      # Unitarios — servicio platos del frontend
│
├── e2e/
│   ├── playwright.config.ts                   # Configuración de Playwright
│   ├── package.json                           # Dependencias E2E
│   └── tests/
│       ├── helpers.ts                         # Funciones auxiliares (login, logout, etc.)
│       ├── smoke.spec.ts                      # Pruebas de humo (carga de páginas)
│       ├── auth.spec.ts                       # Flujo de autenticación E2E
│       └── crud.spec.ts                       # CRUD completo (categorías + platos)
│
└── .github/workflows/
    └── api-tests.yml                          # Pipeline CI con 3 jobs
```

---

## 3. Niveles de Prueba

### 3.1 Pruebas Unitarias de Servicios (ApiRestaurante)

**Ubicación:** `ApiRestaurante/tests/test_services_*.py`  
**Técnica:** Mocks con `unittest.mock.Mock` y `monkeypatch` de pytest  
**BD requerida:** ❌ No  

Estas pruebas validan la **lógica de negocio** de la capa de servicios, aislándola completamente de la base de datos y dependencias externas.

#### `test_services_auth_service.py` (4 tests)

| # | Caso de Prueba | Qué valida |
|---|---|---|
| 1 | `test_register_user_raises_when_username_exists` | Que al intentar registrar un usuario con nombre de usuario ya existente, se lanza la excepción `UsernameAlreadyExists` |
| 2 | `test_register_user_raises_when_email_exists` | Que al intentar registrar con un email ya existente, se lanza la excepción `EmailAlreadyExists` |
| 3 | `test_register_user_success_calls_repo` | Que al registrar con datos válidos, se invoca `users_repo.create` con `nombre_completo`, `usuario`, `email`, `rol` y `password_hash` |
| 4 | `test_authenticate_invalid_password` | Que al autenticar con contraseña incorrecta, se lanza la excepción `InvalidCredentials` |

**Mocks utilizados:**
- `users_repo.get_by_username` → simula que el usuario existe o no
- `users_repo.get_by_email` → simula que el email existe o no
- `users_repo.create` → verifica parámetros de creación
- `verify_password` → simula que la contraseña es incorrecta

#### `test_services_category_service.py` (2 tests)

| # | Caso de Prueba | Qué valida |
|---|---|---|
| 1 | `test_create_category_raises_when_name_exists` | Que al crear una categoría con nombre duplicado (case-insensitive), se lanza `CategoryNameAlreadyExists` |
| 2 | `test_create_category_calls_repo_create` | Que cuando el nombre es único, se invoca `categories_repo.create` con los parámetros correctos |

#### `test_services_menu_service.py` (2 tests)

| # | Caso de Prueba | Qué valida |
|---|---|---|
| 1 | `test_get_public_menu_summary_raises_if_restaurant_missing` | Que al consultar un restaurante inexistente, se lanza `RestaurantNotFound` |
| 2 | `test_get_public_menu_summary_counts_categories` | Que el resumen del menú incluye el conteo correcto de categorías |

#### `test_services_restaurant_service.py` (2 tests)

| # | Caso de Prueba | Qué valida |
|---|---|---|
| 1 | `test_create_restaurant_raises_when_slug_exists` | Que al crear un restaurante con slug duplicado, se lanza `RestaurantSlugAlreadyExists` |
| 2 | `test_create_restaurant_returns_payload_when_slug_free` | Que cuando el slug es libre, se retorna el payload correcto con todos los campos |

---

### 3.2 Pruebas de Repositorios (ApiRestaurante)

**Ubicación:** `ApiRestaurante/tests/test_repositories_*.py`  
**Técnica:** Pruebas de integración contra Postgres real  
**BD requerida:** ✅ Postgres (vía `DATABASE_URL`)  

Estas pruebas validan que la **capa de acceso a datos** (SQLAlchemy) interactúa correctamente con la base de datos PostgreSQL real. Cada test crea datos, los consulta y verifica la integridad.

#### `test_repositories_users.py` (3 tests)

| # | Caso de Prueba | Qué valida |
|---|---|---|
| 1 | `test_users_create_and_get_by_username` | Crear un usuario y luego recuperarlo por nombre de usuario. Verifica que el `id` y `usuario` coinciden |
| 2 | `test_users_get_by_email` | Crear un usuario con email y recuperarlo con `get_by_email`. Verifica búsqueda case-insensitive |
| 3 | `test_users_get_by_email_not_found` | Que `get_by_email` retorna `None` cuando no hay coincidencia |

#### `test_repositories_restaurants.py` (2 tests)

| # | Caso de Prueba | Qué valida |
|---|---|---|
| 1 | `test_restaurants_list_slugs` | Crear dos restaurantes y verificar que `list_slugs` retorna los slugs ordenados alfabéticamente |
| 2 | `test_restaurants_get_by_slug` | Crear un restaurante y recuperarlo por slug. Verifica que el slug coincide |

#### `test_repositories_categories.py` (2 tests)

| # | Caso de Prueba | Qué valida |
|---|---|---|
| 1 | `test_categories_create_and_list_by_restaurant` | Crear dos categorías con distinta posición y verificar que `list_by_restaurant_id` las retorna ordenadas por posición |
| 2 | `test_categories_get_by_id` | Crear una categoría y recuperarla por ID. Verifica que el nombre coincide |

#### `test_repositories_dishes.py` (2 tests)

| # | Caso de Prueba | Qué valida |
|---|---|---|
| 1 | `test_dishes_create_and_list_by_category` | Crear dos platos con distinta posición y verificar que `list_by_category_id` los retorna ordenados por posición |
| 2 | `test_dishes_get_by_id` | Crear un plato y recuperarlo por ID. Verifica que el nombre coincide |

**Aislamiento de datos:**  
Después de cada test, el fixture `_clean_db` (autouse) ejecuta `TRUNCATE TABLE ... RESTART IDENTITY CASCADE` en todas las tablas para garantizar aislamiento total entre tests.

---

### 3.3 Pruebas de Contrato API (ApiRestaurante)

**Ubicación:** `ApiRestaurante/tests/test_api_*.py`  
**Técnica:** FastAPI `TestClient` (in-process, sin red)  
**BD requerida:** ✅ Postgres (vía dependency override de `get_db`)  

Estas pruebas validan los **endpoints HTTP** de la API REST. Utilizan `TestClient` de FastAPI que ejecuta la aplicación en el mismo proceso, sin levantar un servidor real, pero con la base de datos PostgreSQL conectada.

#### `test_api_auth_login.py` (3 tests)

| # | Caso de Prueba | Endpoint | Método | Status esperado | Qué valida |
|---|---|---|---|---|---|
| 1 | `test_auth_login_success_returns_token` | `/api/v1/auth/login` | POST | 200 | Login exitoso retorna `access_token`, `token_type: bearer` y `rol` |
| 2 | `test_auth_login_unknown_user_is_404` | `/api/v1/auth/login` | POST | 404 | Usuario inexistente retorna 404 |
| 3 | `test_auth_login_wrong_password_is_401` | `/api/v1/auth/login` | POST | 401 | Contraseña incorrecta retorna 401 |

#### `test_api_auth_register.py` (8 tests) — RF02

| # | Caso de Prueba | Endpoint | Método | Status esperado | Qué valida |
|---|---|---|---|---|---|
| 1 | `test_register_success` | `/api/v1/auth/register` | POST | 200 | Registro exitoso retorna `message`, `user_id` y `rol` |
| 2 | `test_register_duplicate_username` | `/api/v1/auth/register` | POST | 400 | Usuario duplicado retorna 400 con `detail: "Usuario ya existe"` |
| 3 | `test_register_duplicate_email` | `/api/v1/auth/register` | POST | 400 | Email duplicado retorna 400 con `detail: "El email ya está registrado"` |
| 4 | `test_register_missing_nombre` | `/api/v1/auth/register` | POST | 422 | Nombre vacío falla la validación Pydantic |
| 5 | `test_register_invalid_email` | `/api/v1/auth/register` | POST | 422 | Email sin formato válido falla la validación |
| 6 | `test_register_short_password` | `/api/v1/auth/register` | POST | 422 | Contraseña menor a 6 caracteres falla la validación |
| 7 | `test_register_short_username` | `/api/v1/auth/register` | POST | 422 | Usuario menor a 3 caracteres falla la validación |
| 8 | `test_register_then_login` | `/api/v1/auth/register` + `/api/v1/auth/login` | POST | 200 | Flujo completo: registrar usuario y luego autenticarse exitosamente |

#### `test_api_contract_public_menu.py` (3 tests)

| # | Caso de Prueba | Endpoint | Método | Status esperado | Qué valida |
|---|---|---|---|---|---|
| 1 | `test_public_menu_restaurants_contract` | `/api/v1/public/menu/restaurants` | GET | 200 | Retorna lista con al menos 1 restaurante, cada uno con `id`, `nombre`, `slug` |
| 2 | `test_public_menu_by_slug_contract` | `/api/v1/public/menu/{slug}` | GET | 200 | Retorna estructura completa: `restaurant.slug`, lista de `categorias`, cada categoría con `platos` |
| 3 | `test_public_menu_unknown_slug_is_404` | `/api/v1/public/menu/{slug}` | GET | 404 | Slug inexistente retorna 404 con `detail` |

---

### 3.4 Pruebas Unitarias de Servicios (AppRestaurante)

**Ubicación:** `AppRestaurante/tests/test_services_*.py`  
**Técnica:** Mocks con `monkeypatch` y objetos `_FakeResponse`  
**BD requerida:** ❌ No  

Estas pruebas validan la capa de servicios del **frontend** (AppRestaurante), que se comunica con la API backend vía HTTP. Se simula la respuesta HTTP del backend con objetos `_FakeResponse`.

#### `test_services_auth_service.py` (8 tests)

| # | Caso de Prueba | Qué valida |
|---|---|---|
| 1 | `test_autenticar_usuario_success` | Login exitoso: verifica que `token`, `rol`, `user_id`, `restaurant_id`, `restaurant_slug` se extraen correctamente del JSON del backend. También valida que el token se limpia de espacios |
| 2 | `test_autenticar_usuario_invalid_credentials` | Credenciales inválidas (401): retorna `{"error": "Credenciales inválidas"}` |
| 3 | `test_register_owner_with_restaurant_backend_error_detail` | Error del backend (400): extrae el `detail` del JSON de error |
| 4 | `test_register_owner_with_restaurant_connection_error` | Error de conexión al backend: retorna `{"error": "No se pudo conectar al servidor"}` |
| 5 | `test_register_client_success` | Registro de cliente exitoso: verifica que retorna `{"ok": True}` y envía los campos correctos al backend |
| 6 | `test_register_client_duplicate_error` | Registro con datos duplicados (400): retorna el mensaje de error del backend |
| 7 | `test_register_client_validation_error` | Validación fallida (422): retorna mensaje genérico "Datos inválidos" |
| 8 | `test_register_client_connection_error` | Error de conexión: retorna `{"error": "No se pudo conectar al servidor"}` |

#### `test_services_categoria_service.py` (3 tests)

| # | Caso de Prueba | Qué valida |
|---|---|---|
| 1 | `test_get_headers_strips_quotes_and_spaces` | Que la función `get_headers` limpia comillas y espacios del token antes de generar el header `Authorization: Bearer ...` |
| 2 | `test_list_categorias_non_200_returns_error` | Que un status != 200 retorna `{"error": True, "status_code": 401}` |
| 3 | `test_create_categoria_http_401_message` | Que un 401 retorna un mensaje con "Token inválido" |

#### `test_services_menu_service.py` (3 tests)

| # | Caso de Prueba | Qué valida |
|---|---|---|
| 1 | `test_list_public_restaurants_returns_list` | Que una respuesta 200 retorna una lista de restaurantes con `slug` y `nombre` |
| 2 | `test_list_public_restaurants_handles_non_200` | Que un status 500 retorna una lista vacía `[]` (graceful degradation) |
| 3 | `test_get_public_menu_non_200_returns_none` | Que un status 404 retorna `None` |

#### `test_services_dish_service.py` (3 tests)

| # | Caso de Prueba | Qué valida |
|---|---|---|
| 1 | `test_get_headers_strips_quotes` | Que `get_headers` limpia comillas del token |
| 2 | `test_create_dish_returns_error_on_500` | Que un error 500 retorna `{"error": True, "status_code": 500}` |
| 3 | `test_toggle_availability_non_200` | Que un 404 al cambiar disponibilidad retorna `{"error": True, "status_code": 404}` |

---

### 3.5 Pruebas E2E con Playwright

**Ubicación:** `e2e/tests/*.spec.ts`  
**Técnica:** Playwright con Chromium (navegador real)  
**Infraestructura:** Docker Compose completo (postgres + backend + frontend)  

Estas pruebas validan el **flujo completo del usuario** desde el navegador, interactuando con la interfaz web real.

#### `smoke.spec.ts` — Pruebas de Humo (5 tests)

| # | Caso de Prueba | Qué valida |
|---|---|---|
| 1 | `home loads and has navbar brand` | La página principal carga y muestra el enlace "Restaurante" en la barra de navegación |
| 2 | `security: protected pages redirect to login when logged out` | Las páginas protegidas (`/categories`, `/platos`) redirigen al login cuando no hay sesión activa |
| 3 | `public menu index loads and can open menu` | La página `/menu` carga, muestra el encabezado "Menú Público", y al seleccionar un restaurante se puede ver el menú con sus categorías y platos |
| 4 | `visual/layout sanity: login form has aligned controls` | El formulario de login tiene campos `usuario` y `password` visibles y con ancho mayor a 200px (validación de layout) |

#### `auth.spec.ts` — Flujo de Autenticación (2 tests)

| # | Caso de Prueba | Qué valida |
|---|---|---|
| 1 | `register owner -> can login -> logout redirects protected pages` | **Flujo completo:** Registrar nuevo propietario con restaurante → Login exitoso → Acceder a página protegida (`/restaurants`) → Logout → Verificar que páginas protegidas redirigen al login |
| 2 | `login failure shows error` | Login con credenciales incorrectas muestra alerta de error visible (`.alert.alert-danger`) |

**Aislamiento:** Cada ejecución genera un usuario y slug únicos usando `uniqueSuffix()` (timestamp + random), evitando colisiones entre ejecuciones.

#### `crud.spec.ts` — CRUD Completo (1 test con múltiples pasos)

| # | Caso de Prueba | Pasos | Qué valida |
|---|---|---|---|
| 1 | `CRUD happy path (category + dish)` | 8 pasos | Flujo CRUD completo de administración |

**Desglose del flujo CRUD:**

| Paso | Acción | Verificación |
|---|---|---|
| 1 | Registrar nuevo propietario vía `/registro` | Formulario se envía sin error |
| 2 | Login con el nuevo usuario | Se accede a `/restaurants` correctamente |
| 3 | Crear categoría vía `/categories` | La tabla `#categoriasTable` contiene el nombre de la categoría |
| 4 | Crear plato vía `/platos` (modal) | La tarjeta `.plato-card` contiene el nombre del plato |
| 5 | Cambiar disponibilidad del plato (toggle) | Se muestra alerta "disponibilidad actualizada" |
| 6 | Eliminar plato (con diálogo de confirmación) | La tarjeta del plato desaparece (count = 0) |
| 7 | Eliminar categoría (con diálogo de confirmación) | La tabla ya no contiene el nombre de la categoría |

---

## 4. Infraestructura de Pruebas

### 4.1 Fixtures y `conftest.py`

**Archivo:** `ApiRestaurante/tests/conftest.py`

| Fixture | Scope | Descripción |
|---|---|---|
| `engine` | `session` | Crea el engine SQLAlchemy con `DATABASE_URL` y ejecuta `Base.metadata.create_all` una vez |
| `db_session` | `function` | Crea una sesión nueva para cada test |
| `client` | `function` | FastAPI `TestClient` con dependency override de `get_db` |
| `make_user` | `function` | Factory para crear usuarios con datos por defecto configurables |
| `make_restaurant` | `function` | Factory para crear restaurantes asociados a un admin |
| `make_category` | `function` | Factory para crear categorías asociadas a un restaurante |
| `make_dish` | `function` | Factory para crear platos asociados a una categoría |
| `_clean_db` | `function` (autouse) | Ejecuta `TRUNCATE ... CASCADE` después de cada test |

**Patrón de Factory:**  
Cada factory (`make_user`, `make_restaurant`, etc.) acepta parámetros con valores por defecto, permitiendo crear datos con una sola línea:
```python
admin = make_user(usuario="admin", rol="admin")
restaurant = make_restaurant(admin_id=admin.id, slug="mi-restaurante")
```

### 4.2 Helpers de Playwright

**Archivo:** `e2e/tests/helpers.ts`

| Función | Descripción |
|---|---|
| `gotoAndExpectOk(page, url)` | Navega a la URL y verifica que el status HTTP sea < 500 |
| `uiLogin(page, usuario, password)` | Realiza login vía UI: llena formulario, hace clic, espera redirección, y valida acceso a página protegida |
| `logout(page)` | Navega a `/api/v1/auth/logout` |
| `expectRedirectToLogin(page)` | Verifica que la página actual es el login o muestra mensaje 401 |
| `uniqueSuffix()` | Genera sufijo único con `Date.now()` + random para aislar datos entre ejecuciones |

**Robustez del `uiLogin`:**  
Implementa un polling con timeout de 30s que espera hasta que el navegador salga de la URL de login o aparezca un error, manejando la latencia de contenedores en CI.

### 4.3 Configuración de Playwright

**Archivo:** `e2e/playwright.config.ts`

| Parámetro | Valor | Nota |
|---|---|---|
| `baseURL` | `E2E_BASE_URL` o `http://localhost:8000` | Configurable por variable de entorno |
| `timeout` | 60s | Timeout global por test |
| `expect.timeout` | 10s | Timeout para assertions |
| `retries` | 2 en CI, 0 en local | Reintentos automáticos en CI |
| `trace` | `on-first-retry` | Captura traza de Playwright en primer reintento |
| `screenshot` | `only-on-failure` | Captura screenshot solo cuando falla |
| `video` | `retain-on-failure` | Graba video solo cuando falla |
| `browser` | Chromium | Un solo navegador (Desktop Chrome) |
| **Reporters CI** | `line` + `junit` + `html` | JUnit XML para integración CI + reporte HTML |

---

## 5. Integración Continua (CI)

### 5.1 Workflow: `api-tests.yml`

**Triggers:**
- `push` a branches: `main`
- `pull_request` (cualquier branch)

### 5.2 Jobs del Pipeline

```
┌──────────────────────────────┐
│  apirestaurante-pytest       │  ← Servicios + Repos + Contrato API
│  (Postgres service container)│
└──────────────────────────────┘

┌──────────────────────────────┐
│  apprestaurante-pytest       │  ← Servicios del frontend (sin BD)
│  (solo Python + mocks)       │
└──────────────────────────────┘

┌──────────────────────────────┐
│  playwright-e2e              │  ← E2E con Docker Compose completo
│  (docker compose up)         │
└──────────────────────────────┘
```

Los tres jobs se ejecutan **en paralelo**.

#### Job 1: `apirestaurante-pytest`

| Paso | Descripción |
|---|---|
| Service container | Postgres 15 con credenciales desde `secrets` |
| Health-check | `pg_isready` (verifica disponibilidad del servidor) |
| Build DATABASE_URL | Construye la URL a partir de variables de entorno del job |
| Python 3.13 | Setup del intérprete |
| Install deps | `requirements.txt` + `pytest` + `pytest-asyncio` |
| Run service tests | `pytest tests/test_services_*.py` |
| Run repository tests | `pytest tests/test_repositories_*.py` |
| Run API contract tests | `pytest tests/test_api_*.py` |

#### Job 2: `apprestaurante-pytest`

| Paso | Descripción |
|---|---|
| Python 3.13 | Setup del intérprete |
| Install deps | `requirements.txt` + `pytest` |
| Run tests | `pytest` (todos los tests en `AppRestaurante/tests/`) |

#### Job 3: `playwright-e2e`

| Paso | Descripción |
|---|---|
| Node.js 20 | Setup del runtime |
| Install E2E deps | `npm ci` |
| Install browsers | `npx playwright install --with-deps` |
| Build DATABASE_URL | URL con host `postgres_db` (nombre del servicio Docker) |
| Boot app | `docker compose up -d --build` |
| Wait for frontend | Polling HTTP hasta que `http://localhost:8000` responda con status < 500 (timeout: 120s) |
| Diagnostics | Validación exhaustiva de rutas, auth y logs (ejecuta siempre) |
| Run Playwright tests | `npm run test:ci` |
| Upload report | Artefacto `playwright-report` con screenshots, videos y trazas |
| Dump logs on failure | Logs de Docker Compose si falla algún test |
| Shutdown | `docker compose down -v` |

### 5.3 Gestión de Secretos

Todas las credenciales de base de datos se manejan como **GitHub Secrets**:

| Secreto | Uso |
|---|---|
| `POSTGRES_USER` | Usuario de PostgreSQL |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL |
| `POSTGRES_DB` | Nombre de la base de datos |

**Dónde se inyectan:**

| Contexto del workflow | Fuente | Soportado |
|---|---|---|
| `jobs.<id>.env` | `secrets.*` | ✅ |
| `services.<id>.env` | `secrets.*` | ✅ |
| `services.<id>.options` | Literal (sin expresiones) | ⚠️ Solo literales |
| `steps.<id>.env` | `secrets.*` vía `$GITHUB_ENV` | ✅ |

> **Nota:** El campo `options` de service containers en GitHub Actions **no soporta** ningún contexto de expresión (`secrets`, `env`, `vars`). Por eso el health-check usa `pg_isready` sin parámetros.

---

## 6. Ejecución Local

### Prerrequisitos

1. Archivo `.env` en la raíz del proyecto (ver `.env.example`):
   ```
   POSTGRES_USER=tu_usuario
   POSTGRES_PASSWORD=tu_contraseña
   POSTGRES_DB=tu_base_de_datos
   DATABASE_URL=postgresql+psycopg2://tu_usuario:tu_contraseña@localhost:5432/tu_base_de_datos
   ```

2. Docker y Docker Compose instalados

### Ejecutar pruebas unitarias (ApiRestaurante)

```bash
# Sin base de datos — solo servicios
cd ApiRestaurante
python -m pytest tests/test_services_*.py -v
```

### Ejecutar pruebas de repositorio y contrato (ApiRestaurante)

```bash
# Requiere Postgres corriendo (docker compose o local)
cd ApiRestaurante
export DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/db"
python -m pytest tests/test_repositories_*.py tests/test_api_*.py -v
```

### Ejecutar pruebas unitarias (AppRestaurante)

```bash
# Sin base de datos
cd AppRestaurante
python -m pytest -v
```

### Ejecutar pruebas E2E

```bash
# Levantar toda la infraestructura
docker compose up -d --build

# Instalar dependencias E2E
cd e2e
npm ci
npx playwright install --with-deps

# Ejecutar tests
E2E_BASE_URL=http://localhost:8000 npx playwright test

# Con interfaz gráfica
npx playwright test --headed

# Ver reporte
npx playwright show-report
```

---

## 7. Matriz de Cobertura

| Componente | Capa | Tests Unitarios | Tests Integración | Tests E2E |
|---|---|---|---|---|
| **Autenticación (login)** | Backend API | ✅ `test_services_auth_service` | ✅ `test_api_auth_login` | ✅ `auth.spec.ts` |
| **Registro de propietario** | Backend API | ✅ `test_services_auth_service` | ✅ `test_api_auth_register` | ✅ `auth.spec.ts` |
| **Registro de cliente (RF02)** | Backend API | ✅ `test_services_auth_service` | ✅ `test_api_auth_register` | — |
| **Restaurantes (CRUD)** | Backend API | ✅ `test_services_restaurant_service` | ✅ `test_repositories_restaurants` | — |
| **Categorías (CRUD)** | Backend API | ✅ `test_services_category_service` | ✅ `test_repositories_categories` | ✅ `crud.spec.ts` |
| **Platos (CRUD)** | Backend API | — | ✅ `test_repositories_dishes` | ✅ `crud.spec.ts` |
| **Menú público** | Backend API | ✅ `test_services_menu_service` | ✅ `test_api_contract_public_menu` | ✅ `smoke.spec.ts` |
| **Auth frontend** | Frontend | ✅ `test_services_auth_service` | — | ✅ `auth.spec.ts` |
| **Categorías frontend** | Frontend | ✅ `test_services_categoria_service` | — | ✅ `crud.spec.ts` |
| **Platos frontend** | Frontend | ✅ `test_services_dish_service` | — | ✅ `crud.spec.ts` |
| **Menú frontend** | Frontend | ✅ `test_services_menu_service` | — | ✅ `smoke.spec.ts` |
| **Seguridad (redirect a login)** | Frontend | — | — | ✅ `smoke.spec.ts` |
| **Layout visual** | Frontend | — | — | ✅ `smoke.spec.ts` |

---

## 8. Resumen de Casos de Prueba

### ApiRestaurante — Servicios (10 tests, sin BD)

| Archivo | Test | Resultado esperado |
|---|---|---|
| `test_services_auth_service.py` | `test_register_user_raises_when_username_exists` | `UsernameAlreadyExists` |
| `test_services_auth_service.py` | `test_register_user_raises_when_email_exists` | `EmailAlreadyExists` |
| `test_services_auth_service.py` | `test_register_user_success_calls_repo` | Invoca `users_repo.create` con todos los campos |
| `test_services_auth_service.py` | `test_authenticate_invalid_password` | `InvalidCredentials` |
| `test_services_category_service.py` | `test_create_category_raises_when_name_exists` | `CategoryNameAlreadyExists` |
| `test_services_category_service.py` | `test_create_category_calls_repo_create` | Retorna categoría creada |
| `test_services_menu_service.py` | `test_get_public_menu_summary_raises_if_restaurant_missing` | `RestaurantNotFound` |
| `test_services_menu_service.py` | `test_get_public_menu_summary_counts_categories` | `categories_count == 3` |
| `test_services_restaurant_service.py` | `test_create_restaurant_raises_when_slug_exists` | `RestaurantSlugAlreadyExists` |
| `test_services_restaurant_service.py` | `test_create_restaurant_returns_payload_when_slug_free` | Payload con slug, admin_id, telefono |

### ApiRestaurante — Repositorios (9 tests, con Postgres)

| Archivo | Test | Resultado esperado |
|---|---|---|
| `test_repositories_users.py` | `test_users_create_and_get_by_username` | Usuario creado y recuperado por username |
| `test_repositories_users.py` | `test_users_get_by_email` | Usuario recuperado por email (case-insensitive) |
| `test_repositories_users.py` | `test_users_get_by_email_not_found` | `None` cuando el email no existe |
| `test_repositories_restaurants.py` | `test_restaurants_list_slugs` | Slugs ordenados alfabéticamente |
| `test_repositories_restaurants.py` | `test_restaurants_get_by_slug` | Restaurante recuperado por slug |
| `test_repositories_categories.py` | `test_categories_create_and_list_by_restaurant` | Categorías ordenadas por posición |
| `test_repositories_categories.py` | `test_categories_get_by_id` | Categoría recuperada por ID |
| `test_repositories_dishes.py` | `test_dishes_create_and_list_by_category` | Platos ordenados por posición |
| `test_repositories_dishes.py` | `test_dishes_get_by_id` | Plato recuperado por ID |

### ApiRestaurante — Contrato API (14 tests, con Postgres)

| Archivo | Test | Endpoint | Status |
|---|---|---|---|
| `test_api_auth_login.py` | `test_auth_login_success_returns_token` | `POST /api/v1/auth/login` | 200 |
| `test_api_auth_login.py` | `test_auth_login_unknown_user_is_404` | `POST /api/v1/auth/login` | 404 |
| `test_api_auth_login.py` | `test_auth_login_wrong_password_is_401` | `POST /api/v1/auth/login` | 401 |
| `test_api_auth_register.py` | `test_register_success` | `POST /api/v1/auth/register` | 200 |
| `test_api_auth_register.py` | `test_register_duplicate_username` | `POST /api/v1/auth/register` | 400 |
| `test_api_auth_register.py` | `test_register_duplicate_email` | `POST /api/v1/auth/register` | 400 |
| `test_api_auth_register.py` | `test_register_missing_nombre` | `POST /api/v1/auth/register` | 422 |
| `test_api_auth_register.py` | `test_register_invalid_email` | `POST /api/v1/auth/register` | 422 |
| `test_api_auth_register.py` | `test_register_short_password` | `POST /api/v1/auth/register` | 422 |
| `test_api_auth_register.py` | `test_register_short_username` | `POST /api/v1/auth/register` | 422 |
| `test_api_auth_register.py` | `test_register_then_login` | `POST /api/v1/auth/register` + `login` | 200 |
| `test_api_contract_public_menu.py` | `test_public_menu_restaurants_contract` | `GET /api/v1/public/menu/restaurants` | 200 |
| `test_api_contract_public_menu.py` | `test_public_menu_by_slug_contract` | `GET /api/v1/public/menu/{slug}` | 200 |
| `test_api_contract_public_menu.py` | `test_public_menu_unknown_slug_is_404` | `GET /api/v1/public/menu/{slug}` | 404 |

### AppRestaurante — Servicios (17 tests, sin BD)

| Archivo | Test | Resultado esperado |
|---|---|---|
| `test_services_auth_service.py` | `test_autenticar_usuario_success` | Token, rol, IDs extraídos correctamente |
| `test_services_auth_service.py` | `test_autenticar_usuario_invalid_credentials` | `{"error": "Credenciales inválidas"}` |
| `test_services_auth_service.py` | `test_register_owner_with_restaurant_backend_error_detail` | `{"error": "no"}` |
| `test_services_auth_service.py` | `test_register_owner_with_restaurant_connection_error` | `{"error": "No se pudo conectar al servidor"}` |
| `test_services_auth_service.py` | `test_register_client_success` | `{"ok": True}` |
| `test_services_auth_service.py` | `test_register_client_duplicate_error` | Retorna `detail` del error 400 |
| `test_services_auth_service.py` | `test_register_client_validation_error` | `{"error": "Datos inválidos"}` |
| `test_services_auth_service.py` | `test_register_client_connection_error` | `{"error": "No se pudo conectar al servidor"}` |
| `test_services_categoria_service.py` | `test_get_headers_strips_quotes_and_spaces` | `Bearer abc` |
| `test_services_categoria_service.py` | `test_list_categorias_non_200_returns_error` | `{"error": True, "status_code": 401}` |
| `test_services_categoria_service.py` | `test_create_categoria_http_401_message` | Contiene "Token inválido" |
| `test_services_menu_service.py` | `test_list_public_restaurants_returns_list` | Lista con slug y nombre |
| `test_services_menu_service.py` | `test_list_public_restaurants_handles_non_200` | `[]` (graceful degradation) |
| `test_services_menu_service.py` | `test_get_public_menu_non_200_returns_none` | `None` |
| `test_services_dish_service.py` | `test_get_headers_strips_quotes` | `Bearer tok` |
| `test_services_dish_service.py` | `test_create_dish_returns_error_on_500` | `{"error": True, "status_code": 500}` |
| `test_services_dish_service.py` | `test_toggle_availability_non_200` | `{"error": True, "status_code": 404}` |

### E2E — Playwright (7 tests, Docker Compose completo)

| Archivo | Test | Flujo |
|---|---|---|
| `smoke.spec.ts` | `home loads and has navbar brand` | GET / → verificar navbar |
| `smoke.spec.ts` | `security: protected pages redirect to login when logged out` | GET /categories, /platos → redirect login |
| `smoke.spec.ts` | `public menu index loads and can open menu (or shows not found gracefully)` | GET /menu → seleccionar restaurante → ver menú con categorías y platos |
| `smoke.spec.ts` | `visual/layout sanity: login form has aligned controls` | GET /login → verificar que inputs son visibles y tienen ancho > 200px |
| `auth.spec.ts` | `register owner -> can login -> logout redirects protected pages` | Registro → Login → Acceso a /restaurants → Logout → Redirect a login |
| `auth.spec.ts` | `login failure shows error` | Login con credenciales malas → `.alert-danger` visible |
| `crud.spec.ts` | `CRUD happy path (category + dish)` | Registro → Login → Crear categoría → Crear plato → Toggle disponibilidad → Eliminar plato → Eliminar categoría |

---

## 9. Resultados CI — Última Ejecución Exitosa

> **Fecha:** 28 de febrero de 2026  
> **Branch:** `main`  
> **Resultado:** ✅ 57/57 tests pasaron

### Job 1: ApiRestaurante — pytest

```
Step: Run service unit tests (fast)
..........                                                               [100%]
10 passed

PASSED tests/test_services_auth_service.py::test_register_user_raises_when_username_exists
PASSED tests/test_services_auth_service.py::test_register_user_raises_when_email_exists
PASSED tests/test_services_auth_service.py::test_register_user_success_calls_repo
PASSED tests/test_services_auth_service.py::test_authenticate_invalid_password
PASSED tests/test_services_category_service.py::test_create_category_raises_when_name_exists
PASSED tests/test_services_category_service.py::test_create_category_calls_repo_create
PASSED tests/test_services_menu_service.py::test_get_public_menu_summary_raises_if_restaurant_missing
PASSED tests/test_services_menu_service.py::test_get_public_menu_summary_counts_categories
PASSED tests/test_services_restaurant_service.py::test_create_restaurant_raises_when_slug_exists
PASSED tests/test_services_restaurant_service.py::test_create_restaurant_returns_payload_when_slug_free
```

```
Step: Run repository tests (Postgres)
.........                                                                [100%]
9 passed

PASSED tests/test_repositories_categories.py::test_categories_create_and_list_by_restaurant
PASSED tests/test_repositories_categories.py::test_categories_get_by_id
PASSED tests/test_repositories_dishes.py::test_dishes_create_and_list_by_category
PASSED tests/test_repositories_dishes.py::test_dishes_get_by_id
PASSED tests/test_repositories_restaurants.py::test_restaurants_list_slugs
PASSED tests/test_repositories_restaurants.py::test_restaurants_get_by_slug
PASSED tests/test_repositories_users.py::test_users_create_and_get_by_username
PASSED tests/test_repositories_users.py::test_users_get_by_email
PASSED tests/test_repositories_users.py::test_users_get_by_email_not_found
```

```
Step: Run API contract tests (in-process)
..............                                                           [100%]
14 passed

PASSED tests/test_api_auth_login.py::test_auth_login_success_returns_token
PASSED tests/test_api_auth_login.py::test_auth_login_unknown_user_is_404
PASSED tests/test_api_auth_login.py::test_auth_login_wrong_password_is_401
PASSED tests/test_api_auth_register.py::test_register_success
PASSED tests/test_api_auth_register.py::test_register_duplicate_username
PASSED tests/test_api_auth_register.py::test_register_duplicate_email
PASSED tests/test_api_auth_register.py::test_register_missing_nombre
PASSED tests/test_api_auth_register.py::test_register_invalid_email
PASSED tests/test_api_auth_register.py::test_register_short_password
PASSED tests/test_api_auth_register.py::test_register_short_username
PASSED tests/test_api_auth_register.py::test_register_then_login
PASSED tests/test_api_contract_public_menu.py::test_public_menu_restaurants_contract
PASSED tests/test_api_contract_public_menu.py::test_public_menu_by_slug_contract
PASSED tests/test_api_contract_public_menu.py::test_public_menu_unknown_slug_is_404
```

### Job 2: AppRestaurante — pytest

```
Step: Run tests
.................                                                        [100%]
17 passed

PASSED tests/test_services_auth_service.py::test_autenticar_usuario_success
PASSED tests/test_services_auth_service.py::test_autenticar_usuario_invalid_credentials
PASSED tests/test_services_auth_service.py::test_register_owner_with_restaurant_backend_error_detail
PASSED tests/test_services_auth_service.py::test_register_owner_with_restaurant_connection_error
PASSED tests/test_services_auth_service.py::test_register_client_success
PASSED tests/test_services_auth_service.py::test_register_client_duplicate_error
PASSED tests/test_services_auth_service.py::test_register_client_validation_error
PASSED tests/test_services_auth_service.py::test_register_client_connection_error
PASSED tests/test_services_categoria_service.py::test_get_headers_strips_quotes_and_spaces
PASSED tests/test_services_categoria_service.py::test_list_categorias_non_200_returns_error
PASSED tests/test_services_categoria_service.py::test_create_categoria_http_401_message
PASSED tests/test_services_dish_service.py::test_get_headers_strips_quotes
PASSED tests/test_services_dish_service.py::test_create_dish_returns_error_on_500
PASSED tests/test_services_dish_service.py::test_toggle_availability_non_200
PASSED tests/test_services_menu_service.py::test_list_public_restaurants_returns_list
PASSED tests/test_services_menu_service.py::test_list_public_restaurants_handles_non_200
PASSED tests/test_services_menu_service.py::test_get_public_menu_non_200_returns_none
```

### Job 3: Playwright — E2E (docker compose)

```
Step: Run Playwright tests
Running 7 tests using 1 worker

  ✓ [chromium] tests/auth.spec.ts    — register owner -> can login -> logout    (2.806s)
  ✓ [chromium] tests/auth.spec.ts    — login failure shows error                (0.580s)
  ✓ [chromium] tests/crud.spec.ts    — CRUD happy path (category + dish)        (5.922s)
  ✓ [chromium] tests/smoke.spec.ts   — home loads and has navbar brand          (0.358s)
  ✓ [chromium] tests/smoke.spec.ts   — security: protected pages redirect       (0.264s)
  ✓ [chromium] tests/smoke.spec.ts   — public menu index loads and can open     (1.636s)
  ✓ [chromium] tests/smoke.spec.ts   — visual/layout sanity: login form         (0.489s)

  7 passed (14.8s)
```

---

> **Total de casos de prueba: 57 tests** distribuidos en 4 niveles de la pirámide de testing (unitarios de servicios, repositorios, contrato API y E2E), ejecutados automáticamente en CI con cada push a `main` o pull request.
