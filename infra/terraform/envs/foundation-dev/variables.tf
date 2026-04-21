variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "environment" {
  type    = string
  default = "foundation-dev"
}

variable "create_cloud_run" {
  description = "Si true, despliega frontend y backend en Cloud Run"
  type        = bool
  default     = false
}

variable "create_storage" {
  description = "Si true, crea bucket de imagenes en Cloud Storage"
  type        = bool
  default     = true
}

variable "images_bucket_name" {
  description = "Nombre del bucket de imagenes. Si vacio, se autogenera"
  type        = string
  default     = ""
}

variable "frontend_image" {
  description = "Imagen del frontend en Artifact Registry"
  type        = string
  default     = ""

  validation {
    condition     = !var.create_cloud_run || length(trimspace(var.frontend_image)) > 0
    error_message = "Debes definir frontend_image cuando create_cloud_run=true."
  }
}

variable "backend_image" {
  description = "Imagen del backend en Artifact Registry"
  type        = string
  default     = ""

  validation {
    condition     = !var.create_cloud_run || length(trimspace(var.backend_image)) > 0
    error_message = "Debes definir backend_image cuando create_cloud_run=true."
  }
}

variable "frontend_container_port" {
  type    = number
  default = 8000
}

variable "backend_container_port" {
  type    = number
  default = 5000
}

variable "allow_frontend_unauthenticated" {
  type    = bool
  default = true
}

variable "allow_backend_unauthenticated" {
  type    = bool
  default = true
}

variable "frontend_env_vars" {
  description = "Variables de entorno adicionales para frontend"
  type        = map(string)
  default     = {}
}

variable "backend_env_vars" {
  description = "Variables de entorno adicionales para backend"
  type        = map(string)
  default     = {}
}

variable "create_frontend_lb" {
  description = "Si true, crea el load balancer externo HTTP hacia Cloud Run frontend"
  type        = bool
  default     = false
}

variable "create_waf_policy" {
  description = "Si true, crea y asocia politica de Cloud Armor al LB"
  type        = bool
  default     = true
}

variable "frontend_cloud_run_service_name" {
  description = "Nombre del servicio Cloud Run frontend externo. Obligatorio solo si create_frontend_lb=true y create_cloud_run=false"
  type        = string
  default     = ""

  validation {
    condition     = (var.create_frontend_lb && !var.create_cloud_run) ? length(trimspace(var.frontend_cloud_run_service_name)) > 0 : true
    error_message = "Debes definir frontend_cloud_run_service_name cuando create_frontend_lb=true y create_cloud_run=false."
  }
}

variable "subnets" {
  description = "Subredes por capa"
  type = map(object({
    cidr        = string
    region      = string
    description = string
  }))
}

variable "create_cloud_router_nat" {
  type    = bool
  default = true
}

variable "enable_cdn" {
  type    = bool
  default = true
}

variable "enable_https_lb" {
  description = "Habilitar listener HTTPS (443) en el LB frontend"
  type        = bool
  default     = false
}

variable "create_cloud_dns" {
  description = "Crear zona publica y registro A en Cloud DNS para el frontend"
  type        = bool
  default     = true
}

variable "dns_zone_name" {
  description = "Nombre de la zona administrada en Cloud DNS"
  type        = string
  default     = "livemenu-public-zone"
}

variable "dns_domain" {
  description = "Dominio raiz gestionado en Cloud DNS (sin protocolo)"
  type        = string
  default     = ""

  validation {
    condition     = !var.create_cloud_dns || length(trimspace(var.dns_domain)) > 0
    error_message = "Debes definir dns_domain cuando create_cloud_dns=true."
  }
}

variable "frontend_subdomain" {
  description = "Subdominio del frontend"
  type        = string
  default     = "app"

  validation {
    condition     = !var.create_cloud_dns || length(trimspace(var.frontend_subdomain)) > 0
    error_message = "Debes definir frontend_subdomain cuando create_cloud_dns=true."
  }
}

variable "managed_certificate_domains" {
  description = "Dominios para certificado administrado por Google"
  type        = list(string)
  default     = []
}

variable "rate_limit_count" {
  type    = number
  default = 100
}

variable "rate_limit_interval_sec" {
  type    = number
  default = 60
}

variable "create_cloud_sql" {
  description = "Si true, crea instancia de Cloud SQL PostgreSQL"
  type        = bool
  default     = false
}

variable "db_tier" {
  description = "Tier de la instancia de Cloud SQL"
  type        = string
  default     = "db-f1-micro"
}

variable "db_name" {
  description = "Nombre de la base de datos"
  type        = string
  default     = "livemenu"
}

variable "db_user" {
  description = "Usuario de la base de datos"
  type        = string
  default     = "livemenu_user"
}

variable "db_password" {
  description = "Contraseña del usuario de la base de datos"
  type        = string
  sensitive   = true
  default     = ""

  validation {
    condition     = !var.create_cloud_sql || length(trimspace(var.db_password)) > 0
    error_message = "Debes definir db_password cuando create_cloud_sql=true."
  }
}
