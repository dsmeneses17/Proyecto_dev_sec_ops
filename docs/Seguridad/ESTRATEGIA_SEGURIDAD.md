# Documentación de Seguridad - Proyecto DevSecOps Restaurante Digital

## 1. Introducción

Esta documentación detalla los componentes de seguridad implementados en el proyecto Restaurante Digital, incluyendo estrategias de cifrado, esquemas de rotación de claves, configuración del Web Application Firewall (WAF) y otros controles de seguridad aplicados en la arquitectura.

La implementación sigue principios de seguridad como defense in depth, principio de menor privilegio y cifrado end-to-end donde sea aplicable.

---

## 2. Estrategia de Cifrado Utilizada

### 2.1 Autenticación y Autorización (JWT)

- **Algoritmo**: HS256 (HMAC-SHA256) para firma de tokens JWT.
- **Clave Secreta**: Almacenada en Secret Manager de GCP (producción) o variables de entorno (desarrollo).
- **Expiración**: Tokens de acceso expiran en 30 minutos; tokens de refresh en 7 días.
- **Validación**: Cada request protegido valida el JWT en el header `Authorization: Bearer <token>`.
- **Implementación**: Librería `python-jose` para codificación/decodificación.

### 2.2 Hash de Contraseñas

- **Algoritmo**: bcrypt con contexto de PassLib.
- **Configuración**: `CryptContext(schemes=["bcrypt"], deprecated="auto")`.
- **Funciones**: `hash_password()` para almacenar; `verify_password()` para verificación.
- **Ventajas**: Resistente a ataques de fuerza bruta y rainbow tables.

### 2.3 Datos en Tránsito

- **Protocolo**: HTTPS obligatorio en Load Balancer de GCP.
- **Certificados**: Administrados por GCP Certificate Manager.
- **Headers de Seguridad**:
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
  - `X-Frame-Options: SAMEORIGIN`
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy: strict-origin-when-cross-origin`

### 2.4 Datos en Reposo

- **Base de Datos**: Cloud SQL for PostgreSQL con cifrado administrado por plataforma (AES-256).
- **Imágenes**: Google Cloud Storage con cifrado del lado del servidor (SSE).
- **Secretos**: Secret Manager de GCP cifra automáticamente con claves administradas por Google.

---

## 3. Esquema de Rotación de Claves

### 3.1 Claves JWT

- **Rotación Automática**: Implementada mediante Cloud Function `rotate-secret` desplegada en Cloud Run.
- **Trigger**: Ejecutada vía Pub/Sub o manualmente; evita eventos recursivos de Secret Manager.
- **Proceso**: Genera nueva `SECRET_KEY` (64 bytes URL-safe), crea nueva versión en Secret Manager, actualiza servicios Cloud Run con nueva versión.
- **Frecuencia Recomendada**: Cada 90 días o en caso de compromiso.
- **Impacto**: Requiere reinicio de servicios Cloud Run para cargar nueva clave.
- **Mitigación**: Tokens existentes permanecen válidos hasta expiración (30 min max).

### 3.2 Claves de Base de Datos y APIs

- **Almacenamiento**: Secret Manager de GCP con versionado automático.
- **Rotación Automática**: La contraseña de DB se rota mediante Cloud Function `rotate-secret`.
- **Proceso**: Genera nueva contraseña segura (32 caracteres con mayúsculas, minúsculas, dígitos y símbolos), actualiza usuario en Cloud SQL, crea nueva versión en Secret Manager.
- **Características de Contraseña**: Cumple políticas de complejidad (mínimo 12 caracteres, mezcla de tipos).
- **Versionado**: Secret Manager mantiene versiones históricas para rollback.
- **Actualización de Servicios**: Cloud Run backend se refresca automáticamente con nueva versión de secreto.

### 3.3 Cloud Function rotate-secret

- **Ubicación**: Desplegada como Cloud Function en GCP.
- **Funcionalidades**:
  - Generación de secretos seguros usando `secrets.token_urlsafe()` para JWT y algoritmo personalizado para DB.
  - Integración con Secret Manager para versionado.
  - Actualización automática de usuarios Cloud SQL vía API.
  - Refresco de servicios Cloud Run mediante actualización de environment variables.
  - Prevención de bucles recursivos detectando eventos de Secret Manager.
- **Variables de Entorno**:
  - `PROJECT_ID`: ID del proyecto GCP.
  - `JWT_SECRET_NAME`: Nombre del secreto JWT (default: "jwt-secret").
  - `DB_SECRET_NAME`: Nombre del secreto DB (default: "db-password").
  - `CLOUD_SQL_INSTANCE`: Nombre de instancia Cloud SQL.
  - `CLOUD_SQL_DB_USER`: Usuario DB a actualizar (default: "livemenu_user").
  - `BACKEND_SERVICE_NAME`, `FRONTEND_SERVICE_NAME`: Servicios Cloud Run a refrescar.
- **Timeouts y Manejo de Errores**: Espera operaciones asíncronas con timeouts configurables.

### 3.4 Claves de Cifrado Administradas (KMS - Opcional)

- **Recomendación**: Usar Cloud KMS para claves de cifrado personalizadas.
- **Beneficios**: Rotación automática, auditoría, separación de duties.
- **Estado Actual**: No implementado; marcado como opcional en arquitectura.

---

## 4. Configuración del Web Application Firewall (WAF)

### 4.1 Cloud Armor (GCP)

- **Ubicación**: Perímetro de red, frente al Global HTTPS Load Balancer.
- **Reglas Implementadas**:

  | Prioridad | Acción | Descripción | Condición |
  |-----------|--------|-------------|-----------|
  | 100 | allow | Permitir tráfico frontend (no-API) | `!request.path.startsWith('/api')` |
  | 850 | allow | Permitir registro de propietarios | `request.path == '/registro'` |
  | 1000 | deny(403) | OWASP SQL Injection | `evaluatePreconfiguredWaf('sqli-v33-stable', {'sensitivity': 2})` |
  | 1010 | deny(403) | OWASP Cross-Site Scripting | `evaluatePreconfiguredWaf('xss-v33-stable', {'sensitivity': 2})` |
  | 1100 | rate_based_ban | Rate Limiting básico | IP-based, 100 req/min, ban 5 min |
  | 2147483647 | allow | Regla por defecto | - |

- **Rate Limiting**:
  - Límite: 100 requests por minuto por IP.
  - Acción excedente: Deny 429 (Too Many Requests).
  - Duración ban: 300 segundos (5 minutos).
  - Implementación: Basada en IP de origen.

### 4.2 Rate Limiting en Aplicación

- **Librería**: `limits` (Python).
- **Configuración**: 100 requests/minute por IP en rutas públicas.
- **Implementación**: Middleware en FastAPI con almacenamiento en memoria.
- **Tests**: Verificación de 429 en exceso de límite.

---

## 5. Otros Componentes de Seguridad

### 5.1 Autenticación y Autorización

- **Registro**: Email y contraseña con validación Pydantic.
- **Login**: Retorna `access_token` + `token_type: bearer`.
- **Roles**: `cliente`, `admin`, `owner` con permisos granulares.
- **Dependencias**: `get_current_user()` valida JWT y extrae claims.

### 5.2 Validación de Entrada

- **Schemas Pydantic**: Validación automática en endpoints.
- **Etiquetas de Platos**: Máximo 10 etiquetas por plato, validadas con `@field_validator`.
- **Imágenes**: Límite 5MB, validación MIME type.

### 5.3 Manejo de Sesiones y Caché

- **Sesiones**: En frontend con manejo seguro.
- **Caché**: In-memory cache con TTL para menús públicos.
- **Invalidación**: Automática en cambios de datos.

### 5.4 Infraestructura Segura

- **Red**: VPC privada con Cloud NAT para outbound.
- **IAM**: Service accounts dedicadas por servicio.
- **Logging**: Cloud Logging con Audit Logs.
- **Monitoring**: Cloud Monitoring con alertas.

### 5.5 Contenedores y CI/CD

- **Escaneo**: Container Scanning en Artifact Registry.
- **Secrets**: No usar `.env` en producción; usar Secret Manager.
- **Builds**: GitHub Actions con dependabot para actualizaciones.

### 5.6 Pruebas de Seguridad

- **Tests Unitarios**: Cobertura de funciones de seguridad (87 tests).
- **Tests E2E**: Playwright para flujos críticos (7 tests).
- **Linters**: ESLint, Pre-commit hooks.

---

## 6. Referencias

- [Arquitectura GCP](ARQUITECTURA_GCP_ENTREGA2.md)
- [Cobertura de Requerimientos](COBERTURA_REQUERIMIENTOS.md)
- [Documentación de Testing](TESTING.md)
- Cloud Function `rotate_secret`: Implementa rotación automática de claves JWT y contraseñas DB.

---

## 7. Problemas Conocidos

### 7.1 Drift en Pipeline de Terraform

- **Descripción**: Existe drift en el pipeline de Terraform causado por imports directos realizados al pipeline, lo que proporciona información específica de recursos a Terraform.
- **Causa**: Los imports directos hacen que Terraform gestione recursos de manera inconsistente con el estado deseado.
- **Impacto Específico**: 
  - Función de rotación de secrets (`rotate-secret`): Genera drift debido a cambios en versiones de secretos.
  - Bucket no utilizado: Un bucket que se dejó de usar durante la rotación de secretos también contribuye al drift.
- **Estado**: El sistema funciona correctamente, pero presenta drift que requiere atención manual.
- **Recomendación**: Revisar y reconciliar el estado de Terraform, evitando imports directos en futuros despliegues para mantener consistencia.