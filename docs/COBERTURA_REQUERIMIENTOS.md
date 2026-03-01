# 5.1 Requerimientos Funcionales — Evidencia de Cobertura

| ID | Categoría | Requerimiento | Prioridad | Estado | Evidencia |
|---|---|---|---|---|---|
| RF-01 | Auth | El sistema debe implementar autenticación mediante JWT | Alta | ✅ | `ApiRestaurante/app/core/security.py` – `create_access_token()`, `decode_token()`, python-jose JWT. Login retorna `access_token` + `token_type: bearer`. Tests: `test_api_auth_login.py` (3 tests) |
| RF-02 | Auth | El sistema debe soportar registro con email y contraseña | Alta | ✅ | `ApiRestaurante/app/routers/auth.py` – endpoints `/register` y `/register-owner`. Schema `UserCreate` valida email con Pydantic `EmailStr`. Tests: `test_api_auth_register.py` (8 tests) |
| RF-03 | Auth | El sistema debe validar JWT en cada request protegido | Alta | ✅ | `AppRestaurante/app/main.py` – middleware `jwt_middleware()` valida token en cada ruta no pública. `ApiRestaurante/app/core/security.py` – dependencia `get_current_user()`. E2E: `auth.spec.ts` |
| RF-04 | Auth | El sistema debe implementar hash seguro de contraseñas (bcrypt) | Alta | ✅ | `AppRestaurante/app/core/security.py` – `CryptContext(schemes=["bcrypt"])`, funciones `hash_password()` y `verify_password()`. Tests: `test_services_auth_service.py` (4 tests) |
| RF-05 | Restaurante | El sistema debe permitir CRUD completo de restaurantes | Alta | ✅ | `ApiRestaurante/app/routers/admin_restaurant.py` – create, read, update, delete. Tests: `test_repositories_restaurants.py` (2 tests), `test_services_restaurant_service.py` (3 tests) |
| RF-06 | Restaurante | El sistema debe generar slug único automáticamente | Alta | ✅ | `ApiRestaurante/app/utils/slug.py` – `slugify()` + `generate_unique_slug()` con deduplicación. Tests: `test_api_slug_auto.py` (4 tests), `test_utils_slug.py` (14 tests) |
| RF-07 | Categorías | El sistema debe permitir CRUD de categorías por restaurante | Alta | ✅ | `ApiRestaurante/app/routers/admin_category.py` – CRUD completo filtrado por `restaurante_id`. Tests: `test_repositories_categories.py` (2 tests), `test_services_category_service.py` (2 tests). E2E: `crud.spec.ts` |
| RF-08 | Categorías | El sistema debe permitir reordenamiento de categorías | Baja | ✅ | `ApiRestaurante/app/routers/admin_category.py` – endpoint `PUT /reorder` actualiza campo `posicion`. Tests: `test_api_categories_reorder.py` (4 tests) |
| RF-09 | Platos | El sistema debe permitir CRUD completo de platos | Alta | ✅ | `ApiRestaurante/app/routers/admin_dish.py` – create, read, update, delete por categoría. Tests: `test_repositories_dishes.py` (2 tests), `test_services_menu_service.py` (2 tests). E2E: `crud.spec.ts` |
| RF-10 | Platos | El sistema debe soportar cambio rápido de disponibilidad | Alta | ✅ | Campo `disponible` (boolean) en modelo `Dish`, actualizable vía endpoint PUT. Frontend: toggle en la UI de platos |
| RF-11 | Platos | El sistema debe soportar precios de oferta | Baja | ✅ | Campo `precio_oferta` (Decimal nullable) en modelo `Dish` y schema `DishBase`. Se muestra en menú público con precio tachado |
| RF-12 | Platos | El sistema debe soportar etiquetas predefinidas | Media | ✅ | Campo `etiquetas` (varchar array) en modelo `Dish`. Schema valida máximo 10 etiquetas por plato con `@field_validator` |
| RF-13 | Imágenes | El sistema debe permitir carga de imágenes hasta 5MB | Alta | ✅ | `AppRestaurante/app/routers/upload.py` – validación `MAX_IMAGE_SIZE`. Config: `IMAGE_MAX_FILE_MB=5` (5 × 1024 × 1024 bytes). Retorna error 400 si excede |
| RF-14 | Imágenes | El sistema debe redimensionar imágenes automáticamente | Media | ✅ | `AppRestaurante/app/services/image_worker_pool.py` – `_render_variant()` usa `Image.thumbnail(LANCZOS)`. 3 variantes: thumbnail (240px), medium (800px), large (1400px) |
| RF-15 | Imágenes | El sistema debe almacenar imágenes en Object Storage | Alta | ✅ | `AppRestaurante/app/services/storage.py` – cliente S3 (boto3), `get_s3_client()`, configuración de bucket vía variables de entorno (`S3_BUCKET_NAME`, `S3_REGION`, etc.) |
| RF-16 | Menú Público | El sistema debe servir menú público sin autenticación | Alta | ✅ | `ApiRestaurante/app/routers/public_menu.py` – sin dependencia de auth. Ruta `/menu/{slug}` incluida en `PUBLIC_PATHS`. Tests: `test_api_contract_public_menu.py` (3 tests) |
| RF-17 | Menú Público | El sistema debe renderizar menú optimizado para móvil | Alta | ✅ | Templates usan Bootstrap 5 responsive grid. `base.html` incluye `<meta name="viewport" content="width=device-width, initial-scale=1.0">`. Diseño mobile-first |
| RF-18 | Menú Público | El sistema debe implementar caché en memoria | Alta | ✅ | `ApiRestaurante/app/cache.py` – clase `InMemoryCache` con TTL configurable. Invalidación via `cache_manager.py`. Tests: `test_cache.py` (8 tests), `test_public_menu_caching.py` (4 tests) |
| RF-19 | QR | El sistema debe generar códigos QR | Alta | ✅ | `AppRestaurante/app/routers/public_menu.py` – `_generate_qr_png_bytes()` usando librería `qrcode`. Genera QR con URL pública del menú |
| RF-20 | QR | El sistema debe soportar personalización de color | Media | ✅ | Campos `qr_color_fg` / `qr_color_bg` (hex) en modelo `Restaurant`. Endpoint `PUT /update-colors`. Colores pasados a `_generate_qr_png_bytes(fill_color, back_color)` |
| RF-21 | QR | El sistema debe exportar QR en PNG y SVG | Alta | ✅ | `_generate_qr_png_bytes()` para PNG + `_generate_qr_svg_bytes()` para SVG usando `qrcode.image.svg.SvgPathImage`. Ambos disponibles en la página QR |
| RF-22 | Analytics | El sistema debe registrar cada visualización del menú | Opcional | ✅ | `POST /api/v1/analytics/views` – registra en tabla `menu_views` (slug, source, user_agent, ip_hash, referrer, viewed_at). Tests: `test_analytics.py` (19 tests) |
| RF-23 | Analytics | El sistema debe mostrar dashboard con métricas básicas | Opcional | ✅ | `GET /api/v1/analytics/stats` – KPIs (total, hoy, 7d, 30d), tendencia diaria (Chart.js), distribución horaria, desglose dispositivo/navegador (doughnuts), exportar CSV |
| RF-24 | Analytics | El sistema debe permitir filtrado por rango de fechas | Opcional | ✅ | Parámetros `start_date` / `end_date` en endpoint stats. Frontend: date picker con validación client-side. Filtro aplica a todos los gráficos y tabla |

## Resumen

- **Total requerimientos**: 24
- **Implementados**: 24 / 24 (100%)
- **Tests backend**: 87 (pytest)
- **Tests E2E**: 7 (Playwright)
- **Cobertura por prioridad**:
  - Alta (16): 16/16 ✅
  - Media (3): 3/3 ✅
  - Baja (2): 2/2 ✅
  - Opcional (3): 3/3 ✅
