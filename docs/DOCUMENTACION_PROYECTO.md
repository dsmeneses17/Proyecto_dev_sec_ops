# Documentación del Proyecto DevSecOps - Restaurante Digital

## 1. Propósito

Este documento consolida la documentación técnica del proyecto Restaurante Digital, incluyendo la arquitectura actual, los controles de seguridad implementados, los nuevos servicios incorporados en GCP y las buenas prácticas aplicadas durante el despliegue y la operación.

El objetivo es dejar una referencia única para entender la solución, su operación y su postura de seguridad.

---

## 2. Resumen ejecutivo

La solución está organizada como una plataforma web desacoplada con tres capas principales:

- Interfaz web para usuarios y administradores.
- API REST para autenticación, lógica de negocio y acceso a datos.
- Capa de persistencia y almacenamiento para datos e imágenes.

En el despliegue local actual, la aplicación corre con Docker Compose sobre los servicios `secure_gateway`, `frontend_api`, `backend_api` y `postgres_db`.

En la arquitectura objetivo de GCP, la solución se apoya en:

- Cloud Run para frontend y backend.
- Cloud SQL for PostgreSQL para persistencia.
- Cloud Storage para imágenes.
- Cloud Armor como WAF.
- Secret Manager para secretos.
- Artifact Registry para imágenes de contenedor.
- VPC, Cloud Router y Cloud NAT para conectividad de red.

---

## 3. Arquitectura actual

### 3.1 Despliegue local / contenedores

El despliegue local se define en [docker-compose.yml](../docker-compose.yml).

Servicios principales:

- `secure_gateway`: Nginx como punto de entrada, con terminación TLS, redirección HTTP a HTTPS y rutas hacia frontend y backend.
- `frontend_api`: aplicación web FastAPI con Jinja2, manejo de sesión, protección HTTPS, rate limiting y subida de imágenes.
- `backend_api`: API FastAPI con autenticación JWT, rate limiting y acceso a PostgreSQL.
- `postgres_db`: PostgreSQL 15 con volumen persistente.

### 3.2 Arquitectura GCP

La arquitectura GCP actual está documentada en [docs/MAPA_ARQUITECTURA.md](MAPA_ARQUITECTURA.md).

Componentes actuales en GCP:

- Global HTTPS Load Balancer.
- Cloud Armor con reglas de protección y rate limiting.
- Serverless NEG hacia Cloud Run.
- Cloud Run frontend y backend.
- Cloud SQL PostgreSQL en configuración regional.
- Cloud Storage para imágenes.
- Secret Manager para secretos.
- Artifact Registry para artefactos de contenedor.
- Cloud Logging, Cloud Monitoring y Audit Logs.
- VPC con subredes, Cloud Router y Cloud NAT.

Importante:

- No se usa Cloud DNS en el entorno actual de Terraform (`create_cloud_dns=false`).

---

## 4. Nuevos servicios incorporados

### 4.1 Cloud Run

Se usa para ejecutar frontend y backend sin administrar servidores.

Beneficios:

- Escalado automático.
- Menor superficie operativa.
- Despliegue consistente por contenedor.
- Aislamiento por servicio.

### 4.2 Cloud Armor

Se usa como WAF para proteger el perímetro.

Controles esperados:

- Protección frente a tráfico malicioso.
- Reglas tipo OWASP.
- Rate limiting para rutas sensibles.

### 4.3 Cloud SQL for PostgreSQL

Se usa como base de datos administrada.

Controles y ventajas:

- Alta disponibilidad regional.
- Backups automáticos.
- Cifrado administrado por plataforma.
- Conectividad controlada desde servicios autorizados.

### 4.4 Cloud Storage

Se usa para almacenar imágenes de menú y variantes de resolución.

Buenas prácticas aplicadas:

- Bucket privado.
- Versionamiento habilitado.
- Separación entre almacenamiento de binarios y datos relacionales.

### 4.5 Secret Manager

Se usa para centralizar secretos como:

- `SECRET_KEY`.
- Contraseña de base de datos.

Beneficios:

- Los secretos no quedan en el repositorio.
- Permite control por IAM.
- Reduce riesgo de exposición accidental.

### 4.6 Artifact Registry

Se usa para almacenar las imágenes de contenedor del frontend y backend.

Beneficios:

- Trazabilidad de versiones.
- Despliegues reproducibles.
- Posibilidad de escaneo de vulnerabilidades en el pipeline.

### 4.7 VPC + Cloud Router + Cloud NAT

Se usa para segmentación de red y salida controlada a Internet.

Beneficios:

- Segmentación por subredes.
- Menor exposición de servicios internos.
- Control de tráfico saliente.

---

## 5. Controles de seguridad implementados

### 5.1 Seguridad de transporte

El proyecto aplica seguridad en tránsito mediante:

- HTTPS obligatorio.
- Redirección HTTP a HTTPS.
- HSTS en el frontend local.
- Terminación TLS en el gateway o en el balanceador.

Evidencia en código:

- [AppRestaurante/app/main.py](../AppRestaurante/app/main.py) aplica redirección HTTPS y HSTS.
- [docker-compose.yml](../docker-compose.yml) publica `80` y `443` en el gateway.
- En GCP, el HTTPS Load Balancer se sitúa como entrada pública.

### 5.2 Autenticación y autorización

La autenticación usa JWT.

Controles relevantes:

- Firma con `SECRET_KEY`.
- Expiración de token.
- Validación de usuario actual desde token.
- Rutas administrativas separadas de rutas públicas.

Evidencia en código:

- [ApiRestaurante/app/core/security.py](../ApiRestaurante/app/core/security.py)
- [AppRestaurante/app/core/security.py](../AppRestaurante/app/core/security.py)

### 5.3 Gestión de secretos

El proyecto exige `SECRET_KEY` en runtime.

Puntos clave:

- Si `SECRET_KEY` no existe, la aplicación falla al iniciar.
- En local se usa `.env`.
- En GCP los secretos deben inyectarse desde Secret Manager.

Evidencia en configuración:

- [ApiRestaurante/app/core/security.py](../ApiRestaurante/app/core/security.py)
- [AppRestaurante/app/core/config.py](../AppRestaurante/app/core/config.py)
- [docker-compose.yml](../docker-compose.yml)
- [infra/terraform/envs/foundation-dev/main.tf](../infra/terraform/envs/foundation-dev/main.tf)

### 5.4 Rate limiting

Ambas aplicaciones incluyen limitación de tasa de 100 solicitudes por minuto por IP.

Objetivo:

- Reducir abuso de API.
- Mitigar tráfico excesivo sobre rutas públicas.

Evidencia:

- [ApiRestaurante/app/main.py](../ApiRestaurante/app/main.py)
- [AppRestaurante/app/main.py](../AppRestaurante/app/main.py)

### 5.5 Cookies seguras y sesión

El frontend usa opciones de seguridad para sesión:

- `SESSION_COOKIE_SECURE=true`
- `SESSION_COOKIE_SAMESITE=lax`

También fuerza redirección HTTPS cuando corresponde.

Evidencia:

- [docker-compose.yml](../docker-compose.yml)
- [AppRestaurante/app/core/config.py](../AppRestaurante/app/core/config.py)

### 5.6 Cabeceras de seguridad

Se agregan cabeceras defensivas para mejorar la postura de seguridad y el puntaje Lighthouse:

- `X-Content-Type-Options: nosniff`
- `Strict-Transport-Security`

Evidencia:

- [AppRestaurante/app/main.py](../AppRestaurante/app/main.py)

### 5.7 Separación de red y exposición mínima

Buenas prácticas aplicadas:

- Backend y frontend no se exponen directamente al host cuando se usan contenedores.
- El punto de entrada es el gateway o el balanceador.
- El backend queda detrás del frontend o detrás del perímetro de GCP.

### 5.8 Control de imágenes

Las imágenes no se almacenan en la base de datos.

Se usa un bucket de objetos para:

- mejor escalabilidad,
- menor tamaño de la BD,
- aislamiento de binarios,
- posibilidad de versionamiento.

---

## 6. Buenas prácticas aplicadas

### 6.1 Principio de menor privilegio

La infraestructura y los servicios usan cuentas dedicadas y permisos acotados.

Ejemplos:

- Cuenta de servicio separada para frontend.
- Cuenta de servicio separada para backend.
- Permisos específicos para Cloud Storage y Secret Manager.

### 6.2 Separación de responsabilidades

El código sigue una separación clara:

- Routers: exposición de endpoints.
- Services: lógica de negocio.
- Repositories: acceso a datos.
- Models: entidades ORM.
- Schemas: contratos de entrada y salida.
- Core: configuración y seguridad.

### 6.3 Configuración por variables de entorno

La configuración sensible o dependiente del entorno no se hardcodea.

Ejemplos:

- `DATABASE_URL`
- `SECRET_KEY`
- `BACKEND_URL`
- `S3_*` y `GCS_*`
- parámetros de worker pool

### 6.4 Contenerización reproducible

Cada servicio tiene su propia imagen y configuración.

Ventajas:

- despliegues repetibles,
- aislamiento de dependencias,
- portabilidad entre local y GCP.

### 6.5 Observabilidad

La solución incorpora trazabilidad operacional con:

- Cloud Logging,
- Cloud Monitoring,
- Audit Logs,
- logs de aplicación y de despliegue.

### 6.6 Resiliencia operativa

Se aplican buenas prácticas para continuidad:

- PostgreSQL con volumen persistente en local.
- HA y backups en Cloud SQL.
- Versionamiento de objetos en Cloud Storage.
- Cierre ordenado del worker de imágenes.

### 6.7 Validación automática

El proyecto cuenta con pruebas y validaciones:

- Pytest para backend y frontend.
- Playwright para E2E.
- Lighthouse para auditoría.
- Ruff para calidad de código.

---

## 7. Flujo funcional

### 7.1 Usuario final

1. Accede a la aplicación web.
2. El gateway o balanceador enruta al frontend.
3. El frontend consulta al backend.
4. El backend valida credenciales y recupera datos.
5. La interfaz presenta el menú o el panel correspondiente.

### 7.2 Administración

1. El usuario autenticado entra a rutas administrativas.
2. El frontend aplica control de sesión y cookies.
3. El backend autoriza el acceso según el JWT.
4. Los datos se persisten en PostgreSQL.

### 7.3 Imágenes

1. El frontend o backend solicita una subida.
2. El archivo se valida por tipo y tamaño.
3. La imagen se procesa en el worker pool.
4. El resultado se almacena en Cloud Storage o en el backend de objetos configurado.

---

## 8. Despliegue y operación

### 8.1 Local

```bash
docker compose --env-file .env up --build -d
docker compose --env-file .env ps
```

### 8.2 Inicialización de base de datos

```bash
docker compose --env-file .env exec backend_api python -m app.z_crearTablas.crearTablas
```

### 8.3 Validación básica

- `https://localhost` debe responder la interfaz web.
- `https://localhost/backend-api/docs` debe mostrar Swagger.
- `http://localhost` debe redirigir a HTTPS.

### 8.4 Terraform

El stack GCP se organiza por capas en `infra/terraform`.

Puntos relevantes:

- `foundation-dev` define la base de red y perímetro.
- `create_cloud_dns=false` en el entorno actual.
- `create_frontend_lb=false` en la fase base.
- `create_waf_policy=true` para política de Cloud Armor.

---

## 9. Evidencia de mejores prácticas

Esta solución ya incorpora varias prácticas recomendadas:

- Seguridad por defecto.
- Secretos fuera del repositorio.
- Aislamiento de servicios.
- Rate limiting en frontend y backend.
- HSTS y redirección HTTPS.
- Componentes desacoplados.
- Infraestructura declarativa con Terraform.
- Contenedores reutilizables.
- Separación entre almacenamiento y base relacional.

---

## 10. Archivos de referencia

- [README.md](../README.md)
- [docs/MAPA_ARQUITECTURA.md](MAPA_ARQUITECTURA.md)
- [docs/arquitectura_gcp_actual.png](arquitectura_gcp_actual.png)
- [docker-compose.yml](../docker-compose.yml)
- [infra/terraform/envs/foundation-dev/README.md](../infra/terraform/envs/foundation-dev/README.md)
- [infra/terraform/envs/foundation-dev/terraform.auto.tfvars](../infra/terraform/envs/foundation-dev/terraform.auto.tfvars)

---

## 11. Conclusión

El proyecto queda documentado como una solución DevSecOps con separación clara entre frontend, backend, base de datos y almacenamiento; controles de seguridad desde la aplicación hasta el perímetro; e infraestructura declarativa preparada para operar en GCP.
