# 📘 Documentación de la API — Restaurante Digital

> **Base URL (local, via gateway HTTPS)**: `https://localhost/backend-api`  
> **Base URL (interna en red Docker)**: `http://backend_api:5000`  
> **Base URL (GCP)**: `https://<lb-domain-o-ip>/backend-api`  
> **Framework**: FastAPI · Python 3.11+  
> **Autenticación**: Bearer Token (JWT)  
> **Rate Limit**: 100 peticiones/minuto por IP (RNF-04)

---

## Índice

1. [Autenticación (`/api/v1/auth`)](#1-autenticación)
2. [Restaurantes — Admin (`/api/v1/admin/restaurants`)](#2-restaurantes--admin)
3. [Categorías — Admin (`/api/v1/admin/categories`)](#3-categorías--admin)
4. [Platos — Admin (`/api/v1/admin/dishes`)](#4-platos--admin)
5. [Menú Público (`/api/v1/public/menu`)](#5-menú-público)
6. [Analíticas (`/api/v1/analytics`)](#6-analíticas)
7. [Modelos de Datos (Schemas)](#7-modelos-de-datos)
8. [Códigos de Error](#8-códigos-de-error)

---

## 1. Autenticación

Prefijo: **`/api/v1/auth`** · Tag: `auth`

### 1.1 Login

| Campo | Valor |
|-------|-------|
| **Método** | `POST` |
| **Ruta** | `/api/v1/auth/login` |
| **Auth** | ❌ No requiere |

**Request Body** (`UserLogin`):

```json
{
  "usuario": "string",
  "password": "string"
}
```

**Response** `200 OK`:

```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user_id": 1,
  "rol": "admin",
  "restaurant_id": "uuid-string | null",
  "restaurant_slug": "mi-restaurante | null"
}
```

**Errores**: `404` usuario no encontrado · `401` credenciales inválidas.

---

### 1.2 Obtener Usuario Actual

| Campo | Valor |
|-------|-------|
| **Método** | `GET` |
| **Ruta** | `/api/v1/auth/me` |
| **Auth** | ✅ Bearer Token |

**Response** `200 OK`: Payload decodificado del JWT (diccionario con `id`, `sub`, `rol`, `restaurant_id`, etc.).

---

### 1.3 Registrar Usuario (Cliente)

| Campo | Valor |
|-------|-------|
| **Método** | `POST` |
| **Ruta** | `/api/v1/auth/register` |
| **Auth** | ❌ No requiere |

**Request Body** (`UserCreate`):

```json
{
  "nombre_completo": "string",
  "usuario": "string (min 3 chars, alfanumérico + _.-)",
  "email": "user@example.com",
  "password": "string (min 6 chars)",
  "rol": "cliente"
}
```

**Response** `200 OK`:

```json
{
  "message": "Usuario registrado",
  "user_id": 1,
  "rol": "cliente"
}
```

**Errores**: `400` usuario o email ya existe · `422` validación fallida.

---

### 1.4 Registrar Propietario + Restaurante

| Campo | Valor |
|-------|-------|
| **Método** | `POST` |
| **Ruta** | `/api/v1/auth/register-owner` |
| **Auth** | ❌ No requiere |

**Request Body** (JSON):

```json
{
  "nombre_completo": "string",
  "usuario": "string",
  "email": "user@example.com",
  "password": "string",
  "restaurant_nombre": "string",
  "restaurant_slug": "string (opcional)",
  "restaurant_telefono": "string (opcional)",
  "restaurant_direccion": "string (opcional)"
}
```

**Response** `200 OK`:

```json
{
  "message": "Registro completado",
  "user_id": 1,
  "restaurant_id": "uuid-string",
  "restaurant_slug": "mi-restaurante"
}
```

**Errores**: `400` usuario/email ya existe · `422` validación fallida.

---

### 1.5 Refrescar Token

| Campo | Valor |
|-------|-------|
| **Método** | `POST` |
| **Ruta** | `/api/v1/auth/refresh` |
| **Auth** | ❌ No requiere |

**Query Params**:

- `refresh_token`: token de refresco (string)

**Response** `200 OK`:

```json
{
  "access_token": "eyJhbGci..."
}
```

**Errores**: `401` token inválido o expirado.

---

## 2. Restaurantes — Admin

Prefijo: **`/api/v1/admin/restaurants`** · Tag: `restaurantes`

> Todos los endpoints requieren autenticación con Bearer Token y rol `admin`.

### 2.1 Obtener Mi Restaurante

| Campo | Valor |
|-------|-------|
| **Método** | `GET` |
| **Ruta** | `/api/v1/admin/restaurants` |
| **Auth** | ✅ Bearer Token |

**Response** `200 OK` → [`RestaurantOut`](#restaurantout)

**Errores**: `404` restaurante no encontrado.

---

### 2.2 Obtener Restaurante por ID

| Campo | Valor |
|-------|-------|
| **Método** | `GET` |
| **Ruta** | `/api/v1/admin/restaurants/restaurant/{restaurant_id}` |
| **Auth** | ✅ Bearer Token |

**Path Params**: `restaurant_id` (UUID)

**Response** `200 OK` → [`RestaurantOut`](#restaurantout)

**Errores**: `404` no encontrado · `403` no autorizado.

---

### 2.3 Crear o Actualizar Restaurante

| Campo | Valor |
|-------|-------|
| **Método** | `POST` |
| **Ruta** | `/api/v1/admin/restaurants/restaurant` |
| **Auth** | ✅ Bearer Token (admin) |

**Request Body** (`RestaurantCreate`):

```json
{
  "id": "uuid (opcional — si se envía, actúa como UPDATE)",
  "nombre": "string (max 100)",
  "descripcion": "string (max 500, opcional)",
  "logo": "https://url (opcional)",
  "telefono": "string (opcional)",
  "direccion": "string (opcional)",
  "horarios": { "lunes": "9-17", "...": "..." },
  "slug": "string (max 100, opcional — se autogenera)",
  "qr_color_fg": "#000000",
  "qr_color_bg": "#FFFFFF"
}
```

**Response** `200 OK` → [`RestaurantOut`](#restaurantout)

**Errores**: `403` no autorizado · `404` id no existe (update) · `400` ya tiene restaurante (create).

---

### 2.4 Actualizar Restaurante (PUT)

| Campo | Valor |
|-------|-------|
| **Método** | `PUT` |
| **Ruta** | `/api/v1/admin/restaurants/restaurant` |
| **Auth** | ✅ Bearer Token (admin) |

**Request Body** (`RestaurantUpdate`): Igual a `RestaurantCreate` pero con `id` obligatorio (UUID).

**Response** `200 OK` → [`RestaurantOut`](#restaurantout)

**Errores**: `404` restaurante no encontrado.

---

### 2.5 Eliminar Restaurante

| Campo | Valor |
|-------|-------|
| **Método** | `DELETE` |
| **Ruta** | `/api/v1/admin/restaurants/restaurant/{restaurant_id}` |
| **Auth** | ✅ Bearer Token (admin) |

**Path Params**: `restaurant_id` (UUID)

**Response** `200 OK`:

```json
{ "message": "Restaurante eliminado correctamente" }
```

**Errores**: `404` no encontrado · `403` no autorizado.

---

### 2.6 Actualizar Colores QR

| Campo | Valor |
|-------|-------|
| **Método** | `PATCH` |
| **Ruta** | `/api/v1/admin/restaurants/restaurant/{restaurant_id}/qr-colors` |
| **Auth** | ✅ Bearer Token (admin) |

**Path Params**: `restaurant_id` (UUID)

**Request Body** (`RestaurantQRColorUpdate`):

```json
{
  "qr_color_fg": "#FF5733",
  "qr_color_bg": "#FFFFFF"
}
```

> Los valores deben cumplir el patrón `^#[0-9A-Fa-f]{6}$`.

**Response** `200 OK` → [`RestaurantOut`](#restaurantout)

**Errores**: `404` no encontrado · `403` no autorizado · `422` formato de color inválido.

---

## 3. Categorías — Admin

Prefijo: **`/api/v1/admin/categories`** · Tag: `categorias`

> Todos los endpoints requieren autenticación con Bearer Token.

### 3.1 Listar Categorías

| Campo | Valor |
|-------|-------|
| **Método** | `GET` |
| **Ruta** | `/api/v1/admin/categories/` |
| **Auth** | ✅ Bearer Token |

**Response** `200 OK` → `list[CategoryOut]`

```json
[
  {
    "id": "uuid",
    "restaurante_id": "uuid",
    "nombre": "Entradas",
    "descripcion": "Aperitivos del chef",
    "posicion": 0,
    "activa": true
  }
]
```

---

### 3.2 Obtener Categoría por ID

| Campo | Valor |
|-------|-------|
| **Método** | `GET` |
| **Ruta** | `/api/v1/admin/categories/{category_id}` |
| **Auth** | ✅ Bearer Token |

**Path Params**: `category_id` (UUID)

**Response** `200 OK` → [`CategoryOut`](#categoryout)

**Errores**: `404` categoría o restaurante no encontrado.

---

### 3.3 Crear Categoría

| Campo | Valor |
|-------|-------|
| **Método** | `POST` |
| **Ruta** | `/api/v1/admin/categories/` |
| **Auth** | ✅ Bearer Token (admin) |

**Request Body** (`CategoryCreate`):

```json
{
  "nombre": "string (max 50)",
  "descripcion": "string (opcional)",
  "posicion": 0,
  "activa": true,
  "restaurante_id": "uuid (opcional)"
}
```

**Response** `200 OK` → [`CategoryOut`](#categoryout)

**Errores**: `403` no autorizado · `404` restaurante no encontrado · `400` nombre duplicado.

---

### 3.4 Actualizar Categoría

| Campo | Valor |
|-------|-------|
| **Método** | `PUT` |
| **Ruta** | `/api/v1/admin/categories/{id}` |
| **Auth** | ✅ Bearer Token (admin) |

**Path Params**: `id` (UUID)

**Request Body** (`CategoryUpdate`):

```json
{
  "nombre": "string (max 50)",
  "descripcion": "string (opcional)",
  "posicion": 1,
  "activa": true
}
```

**Response** `200 OK` → [`CategoryOut`](#categoryout)

**Errores**: `404` categoría no encontrada · `403` no autorizado.

---

### 3.5 Eliminar Categoría

| Campo | Valor |
|-------|-------|
| **Método** | `DELETE` |
| **Ruta** | `/api/v1/admin/categories/{id}` |
| **Auth** | ✅ Bearer Token (admin) |

**Path Params**: `id` (UUID)

**Response** `200 OK`:

```json
{ "message": "Categoría eliminada" }
```

**Errores**: `404` no encontrada · `403` no autorizado.

---

### 3.6 Reordenar Categorías

| Campo | Valor |
|-------|-------|
| **Método** | `PATCH` |
| **Ruta** | `/api/v1/admin/categories/reorder` |
| **Auth** | ✅ Bearer Token (admin) |

**Request Body** (`CategoryReorder`):

```json
{
  "categorias": [
    { "id": "uuid-1", "posicion": 0 },
    { "id": "uuid-2", "posicion": 1 },
    { "id": "uuid-3", "posicion": 2 }
  ]
}
```

**Response** `200 OK`:

```json
{ "message": "Categorías reordenadas correctamente" }
```

**Errores**: `403` no autorizado · `404` restaurante/categoría no encontrada · `400` datos faltantes.

---

## 4. Platos — Admin

Prefijo: **`/api/v1/admin/dishes`** · Tag: `dishes`

> Todos los endpoints requieren autenticación con Bearer Token.

### 4.1 Listar Platos por Categoría

| Campo | Valor |
|-------|-------|
| **Método** | `GET` |
| **Ruta** | `/api/v1/admin/dishes/by_category` |
| **Auth** | ✅ Bearer Token |

**Response** `200 OK`: Lista agrupada por categoría.

```json
[
  {
    "id": "uuid-categoria",
    "nombre": "Entradas",
    "platos": [
      {
        "id": "uuid-plato",
        "nombre": "Ensalada César",
        "descripcion": "...",
        "precio": 15000,
        "precio_oferta": null,
        "categoria_id": "uuid",
        "disponible": true,
        "destacado": false,
        "etiquetas": ["vegano"],
        "posicion": 0,
        "imagen_url": "https://..."
      }
    ]
  }
]
```

---

### 4.2 Listar Todos los Platos

| Campo | Valor |
|-------|-------|
| **Método** | `GET` |
| **Ruta** | `/api/v1/admin/dishes` |
| **Auth** | ✅ Bearer Token |

**Response** `200 OK` → `list[DishOut]`

---

### 4.3 Obtener Plato por ID

| Campo | Valor |
|-------|-------|
| **Método** | `GET` |
| **Ruta** | `/api/v1/admin/dishes/{dish_id}` |
| **Auth** | ✅ Bearer Token |

**Path Params**: `dish_id` (UUID)

**Response** `200 OK` → [`DishOut`](#dishout)

**Errores**: `404` plato no encontrado.

---

### 4.4 Crear Plato

| Campo | Valor |
|-------|-------|
| **Método** | `POST` |
| **Ruta** | `/api/v1/admin/dishes/` |
| **Auth** | ✅ Bearer Token |

**Request Body** (`DishCreate`):

```json
{
  "nombre": "string (max 100)",
  "descripcion": "string (max 300, opcional)",
  "precio": 25000.00,
  "precio_oferta": 20000.00,
  "disponible": true,
  "destacado": false,
  "etiquetas": ["vegano", "sin gluten"],
  "posicion": 1,
  "imagen_url": "https://...",
  "categoria_id": "uuid"
}
```

> **Validaciones**: Máximo 10 etiquetas, cada una máx. 30 caracteres. Se normalizan a minúsculas y se eliminan duplicados.

**Response** `200 OK` → [`DishOut`](#dishout)

---

### 4.5 Actualizar Plato

| Campo | Valor |
|-------|-------|
| **Método** | `PUT` |
| **Ruta** | `/api/v1/admin/dishes/{dish_id}` |
| **Auth** | ✅ Bearer Token |

**Path Params**: `dish_id` (UUID)

**Request Body** (`DishUpdate`): Misma estructura que `DishCreate`.

**Response** `200 OK` → [`DishOut`](#dishout)

**Errores**: `404` plato no encontrado.

---

### 4.6 Eliminar Plato (Soft Delete)

| Campo | Valor |
|-------|-------|
| **Método** | `DELETE` |
| **Ruta** | `/api/v1/admin/dishes/{dish_id}` |
| **Auth** | ✅ Bearer Token |

**Path Params**: `dish_id` (UUID)

> ⚠️ No se elimina de la BD, se marca con `eliminado_en = timestamp`.

**Response** `200 OK`:

```json
{ "detail": "Plato eliminado correctamente" }
```

**Errores**: `404` plato no encontrado.

---

### 4.7 Cambiar Disponibilidad

| Campo | Valor |
|-------|-------|
| **Método** | `PATCH` |
| **Ruta** | `/api/v1/admin/dishes/{dish_id}/toggle_availability` |
| **Auth** | ✅ Bearer Token |

**Path Params**: `dish_id` (UUID)

> Alterna el valor booleano de `disponible`.

**Response** `200 OK` → [`DishOut`](#dishout)

**Errores**: `404` plato no encontrado.

---

## 5. Menú Público

Prefijo: **`/api/v1/public/menu`** · Tag: `public`

> Estos endpoints **no requieren autenticación**. Son consumidos por clientes y visitantes.

### 5.1 Listar Restaurantes Públicos

| Campo | Valor |
|-------|-------|
| **Método** | `GET` |
| **Ruta** | `/api/v1/public/menu/restaurants` |
| **Auth** | ❌ No requiere |

**Response** `200 OK`:

```json
[
  {
    "id": "uuid",
    "nombre": "Mi Restaurante",
    "slug": "mi-restaurante",
    "logo_url": "https://..."
  }
]
```

---

### 5.2 Obtener Menú por Slug

| Campo | Valor |
|-------|-------|
| **Método** | `GET` |
| **Ruta** | `/api/v1/public/menu/{slug}` |
| **Auth** | ❌ No requiere |

**Path Params**: `slug` (string)

> Utiliza caché multi-capa: 1) In-memory → 2) Redis → 3) Base de datos.

**Response** `200 OK`:

```json
{
  "restaurant": {
    "id": "uuid",
    "nombre": "Mi Restaurante",
    "logo_url": "https://...",
    "slug": "mi-restaurante",
    "qr_color_fg": "#000000",
    "qr_color_bg": "#FFFFFF"
  },
  "categorias": [
    {
      "id": "uuid",
      "nombre": "Entradas",
      "platos": [
        {
          "id": "uuid",
          "nombre": "Ensalada César",
          "descripcion": "...",
          "precio": 15000.0,
          "precio_oferta": null,
          "imagen_url": "https://...",
          "destacado": false,
          "etiquetas": ["vegano"]
        }
      ]
    }
  ]
}
```

> Solo devuelve platos con `disponible = true` y `eliminado_en = null`, ordenados por `posicion`.

**Errores**: `404` restaurante no encontrado.

---

## 6. Analíticas

Prefijo: **`/api/v1/analytics`** · Tag: `analytics`

### 6.1 Registrar Vista de Menú

| Campo | Valor |
|-------|-------|
| **Método** | `POST` |
| **Ruta** | `/api/v1/analytics/views` |
| **Auth** | ❌ No requiere |
| **Status** | `201 Created` |

> Se ejecuta automáticamente al cargar un menú público (visitantes anónimos incluidos).

**Request Body** (`MenuViewCreate`):

```json
{
  "slug": "mi-restaurante",
  "source": "menu | qr | direct"
}
```

**Response** `201 Created` → [`MenuViewOut`](#menuviewout)

> Registra automáticamente: `user_agent`, `ip_hash` (SHA-256), `referrer` del request.

**Errores**: `404` restaurante no encontrado.

---

### 6.2 Obtener Estadísticas (Mi Restaurante)

| Campo | Valor |
|-------|-------|
| **Método** | `GET` |
| **Ruta** | `/api/v1/analytics/stats` |
| **Auth** | ✅ Bearer Token (admin) |

**Query Params** (opcionales):

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `start_date` | `YYYY-MM-DD` | Inicio del rango personalizado |
| `end_date` | `YYYY-MM-DD` | Fin del rango personalizado |

**Response** `200 OK` → [`MenuViewStats`](#menuviewstats)

**Errores**: `404` restaurante no encontrado · `400` start_date > end_date.

---

### 6.3 Obtener Estadísticas por Restaurante ID

| Campo | Valor |
|-------|-------|
| **Método** | `GET` |
| **Ruta** | `/api/v1/analytics/stats/{restaurant_id}` |
| **Auth** | ✅ Bearer Token (admin) |

**Path Params**: `restaurant_id` (UUID)

**Query Params**: Igual que [6.2](#62-obtener-estadísticas-mi-restaurante).

**Response** `200 OK` → [`MenuViewStats`](#menuviewstats)

**Errores**: `404` no encontrado · `403` no autorizado · `400` rango inválido.

---

### 6.4 Exportar CSV

| Campo | Valor |
|-------|-------|
| **Método** | `GET` |
| **Ruta** | `/api/v1/analytics/export` |
| **Auth** | ✅ Bearer Token (admin) |

**Query Params** (opcionales):

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `start_date` | `YYYY-MM-DD` | Inicio del rango |
| `end_date` | `YYYY-MM-DD` | Fin del rango |

**Response** `200 OK` → `text/csv` (descarga directa)

Columnas del CSV:

| Columna | Descripción |
|---------|-------------|
| `id` | UUID del registro |
| `slug` | Slug del restaurante |
| `source` | Fuente: `menu`, `qr`, `direct` |
| `user_agent` | User-Agent del navegador |
| `dispositivo` | `Móvil` o `Escritorio` |
| `navegador` | Chrome, Safari, Firefox, Edge, Opera, Otro |
| `referrer` | URL de referencia |
| `viewed_at` | Fecha/hora ISO 8601 |

**Errores**: `404` restaurante no encontrado · `400` rango inválido.

---

## 7. Modelos de Datos

### UserCreate

| Campo | Tipo | Requerido | Validación |
|-------|------|-----------|------------|
| `nombre_completo` | string | ✅ | No vacío |
| `usuario` | string | ✅ | Min 3 chars, `^[a-zA-Z0-9_.-]+$` |
| `email` | EmailStr | ✅ | Formato email válido |
| `password` | string | ✅ | Min 6 caracteres |
| `rol` | string | ❌ | Default: `"cliente"` |

### UserLogin

| Campo | Tipo | Requerido |
|-------|------|-----------|
| `usuario` | string | ✅ |
| `password` | string | ✅ |

### RestaurantOut

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único |
| `nombre` | string | Nombre del restaurante |
| `descripcion` | string \| null | Descripción |
| `telefono` | string \| null | Teléfono de contacto |
| `direccion` | string \| null | Dirección física |
| `horarios` | dict \| null | Horarios de atención |
| `slug` | string \| null | Slug URL-friendly |
| `logo` | string \| null | URL del logo |
| `qr_color_fg` | string | Color QR primer plano (hex) |
| `qr_color_bg` | string | Color QR fondo (hex) |

### RestaurantQRColorUpdate

| Campo | Tipo | Validación |
|-------|------|------------|
| `qr_color_fg` | string | `^#[0-9A-Fa-f]{6}$` |
| `qr_color_bg` | string | `^#[0-9A-Fa-f]{6}$` |

### CategoryOut

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único |
| `restaurante_id` | UUID | FK al restaurante |
| `nombre` | string | Nombre (max 50) |
| `descripcion` | string \| null | Descripción |
| `posicion` | int | Orden de visualización (≥ 0) |
| `activa` | bool | Si está visible |

### CategoryReorder

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `categorias` | list[dict] | `[{"id": "uuid", "posicion": int}]` |

### DishOut

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único |
| `nombre` | string | Nombre (max 100) |
| `descripcion` | string \| null | Descripción (max 300) |
| `precio` | Decimal | Precio base |
| `precio_oferta` | Decimal \| null | Precio de oferta |
| `disponible` | bool | Disponible para mostrar |
| `destacado` | bool | Marcado como destacado |
| `etiquetas` | list[string] \| null | Tags (max 10, cada uno max 30 chars) |
| `posicion` | int \| null | Orden de visualización |
| `imagen_url` | string \| null | URL de la imagen |
| `categoria_id` | UUID | FK a la categoría |
| `creado_en` | datetime \| null | Fecha de creación |
| `actualizado_en` | datetime \| null | Última modificación |
| `eliminado_en` | datetime \| null | Fecha de soft-delete |

### MenuViewCreate

| Campo | Tipo | Validación |
|-------|------|------------|
| `slug` | string | Max 120 chars |
| `source` | string | `^(menu\|qr\|direct)$` |

### MenuViewOut

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único |
| `restaurant_id` | UUID | FK al restaurante |
| `slug` | string | Slug del restaurante |
| `source` | string | Fuente de la vista |
| `user_agent` | string \| null | Navegador del visitante |
| `ip_hash` | string \| null | Hash SHA-256 de la IP |
| `referrer` | string \| null | URL de referencia |
| `viewed_at` | datetime | Timestamp de la visita |

### MenuViewStats

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `restaurant_id` | string | ID del restaurante |
| `slug` | string | Slug del restaurante |
| `total_views` | int | Total de vistas históricas |
| `views_today` | int | Vistas de hoy |
| `views_last_7_days` | int | Vistas últimos 7 días |
| `views_last_30_days` | int | Vistas últimos 30 días |
| `daily_breakdown` | list[DailyStat] | `[{"date": "2025-01-15", "views": 42}]` |
| `hourly_breakdown` | list[HourlyStat] | `[{"hour": 0, "views": 5}, ..., {"hour": 23, "views": 12}]` |
| `device_breakdown` | list[DeviceStat] | `[{"name": "Móvil", "count": 80, "percentage": 65.5}]` |
| `browser_breakdown` | list[DeviceStat] | `[{"name": "Chrome", "count": 50, "percentage": 41.0}]` |
| `start_date` | string \| null | Inicio del rango filtrado |
| `end_date` | string \| null | Fin del rango filtrado |
| `filtered_views` | int \| null | Total en el rango filtrado |

---

## 8. Códigos de Error

| Código | Significado | Detalle |
|--------|-------------|---------|
| `200` | OK | Operación exitosa |
| `201` | Created | Recurso creado (analytics views) |
| `400` | Bad Request | Datos inválidos, duplicados, rango de fechas invertido |
| `401` | Unauthorized | Token ausente, inválido o expirado |
| `403` | Forbidden | Rol insuficiente para la operación |
| `404` | Not Found | Recurso no encontrado |
| `422` | Unprocessable Entity | Error de validación Pydantic |
| `429` | Too Many Requests | Rate limit excedido (100 req/min) |

### Formato de Error Estándar

```json
{
  "detail": "Mensaje descriptivo del error"
}
```

---

## Resumen de Endpoints

| # | Método | Ruta | Auth | Descripción |
|---|--------|------|------|-------------|
| 1 | `POST` | `/api/v1/auth/login` | ❌ | Iniciar sesión |
| 2 | `GET` | `/api/v1/auth/me` | ✅ | Usuario actual |
| 3 | `POST` | `/api/v1/auth/register` | ❌ | Registrar cliente |
| 4 | `POST` | `/api/v1/auth/register-owner` | ❌ | Registrar propietario + restaurante |
| 5 | `POST` | `/api/v1/auth/refresh` | ❌ | Refrescar token |
| 6 | `GET` | `/api/v1/admin/restaurants` | ✅ | Mi restaurante |
| 7 | `GET` | `/api/v1/admin/restaurants/restaurant/{id}` | ✅ | Restaurante por ID |
| 8 | `POST` | `/api/v1/admin/restaurants/restaurant` | ✅ | Crear/actualizar restaurante |
| 9 | `PUT` | `/api/v1/admin/restaurants/restaurant` | ✅ | Actualizar restaurante |
| 10 | `DELETE` | `/api/v1/admin/restaurants/restaurant/{id}` | ✅ | Eliminar restaurante |
| 11 | `PATCH` | `/api/v1/admin/restaurants/restaurant/{id}/qr-colors` | ✅ | Actualizar colores QR |
| 12 | `GET` | `/api/v1/admin/categories/` | ✅ | Listar categorías |
| 13 | `GET` | `/api/v1/admin/categories/{id}` | ✅ | Categoría por ID |
| 14 | `POST` | `/api/v1/admin/categories/` | ✅ | Crear categoría |
| 15 | `PUT` | `/api/v1/admin/categories/{id}` | ✅ | Actualizar categoría |
| 16 | `DELETE` | `/api/v1/admin/categories/{id}` | ✅ | Eliminar categoría |
| 17 | `PATCH` | `/api/v1/admin/categories/reorder` | ✅ | Reordenar categorías |
| 18 | `GET` | `/api/v1/admin/dishes/by_category` | ✅ | Platos por categoría |
| 19 | `GET` | `/api/v1/admin/dishes` | ✅ | Listar platos |
| 20 | `GET` | `/api/v1/admin/dishes/{id}` | ✅ | Plato por ID |
| 21 | `POST` | `/api/v1/admin/dishes/` | ✅ | Crear plato |
| 22 | `PUT` | `/api/v1/admin/dishes/{id}` | ✅ | Actualizar plato |
| 23 | `DELETE` | `/api/v1/admin/dishes/{id}` | ✅ | Eliminar plato (soft) |
| 24 | `PATCH` | `/api/v1/admin/dishes/{id}/toggle_availability` | ✅ | Toggle disponibilidad |
| 25 | `GET` | `/api/v1/public/menu/restaurants` | ❌ | Listar restaurantes públicos |
| 26 | `GET` | `/api/v1/public/menu/{slug}` | ❌ | Menú público por slug |
| 27 | `POST` | `/api/v1/analytics/views` | ❌ | Registrar vista |
| 28 | `GET` | `/api/v1/analytics/stats` | ✅ | Estadísticas mi restaurante |
| 29 | `GET` | `/api/v1/analytics/stats/{id}` | ✅ | Estadísticas por restaurante ID |
| 30 | `GET` | `/api/v1/analytics/export` | ✅ | Exportar CSV |

> **Total: 30 endpoints** · 22 protegidos · 8 públicos
