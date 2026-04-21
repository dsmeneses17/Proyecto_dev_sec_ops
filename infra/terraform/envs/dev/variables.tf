variable "project_id" {
  description = "ID del proyecto GCP"
  type        = string
}

variable "region" {
  description = "Region principal para recursos serverless"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Nombre de entorno"
  type        = string
  default     = "dev"
}

variable "create_storage" {
  description = "Crear bucket de imagenes"
  type        = bool
  default     = true
}

variable "create_cloud_sql" {
  description = "Crear Cloud SQL"
  type        = bool
  default     = true
}

variable "create_secret_manager" {
  description = "Crear secretos en Secret Manager"
  type        = bool
  default     = true
}

variable "create_cloud_armor" {
  description = "Crear politica de Cloud Armor"
  type        = bool
  default     = true
}

variable "frontend_image" {
  description = "Imagen del frontend en Artifact Registry"
  type        = string
}

variable "backend_image" {
  description = "Imagen del backend en Artifact Registry"
  type        = string
}

variable "db_tier" {
  description = "Tier de Cloud SQL"
  type        = string
  default     = "db-custom-2-4096"
}

variable "db_name" {
  description = "Nombre de base de datos de aplicacion"
  type        = string
  default     = "livemenu"
}

variable "db_user" {
  description = "Usuario de base de datos"
  type        = string
  default     = "livemenu_app"
}

variable "db_password" {
  description = "Password del usuario de base de datos"
  type        = string
  default     = ""
  sensitive   = true

  validation {
    condition     = (!var.create_cloud_sql && !var.create_secret_manager) || length(trimspace(var.db_password)) > 0
    error_message = "db_password es obligatorio cuando create_cloud_sql=true o create_secret_manager=true."
  }
}

variable "jwt_secret" {
  description = "Secreto JWT de la aplicacion"
  type        = string
  default     = ""
  sensitive   = true

  validation {
    condition     = !var.create_secret_manager || length(trimspace(var.jwt_secret)) > 0
    error_message = "jwt_secret es obligatorio cuando create_secret_manager=true."
  }
}

variable "backend_env_vars" {
  description = "Variables adicionales para el backend en Cloud Run"
  type        = map(string)
  default     = {}
}

variable "frontend_env_vars" {
  description = "Variables adicionales para el frontend en Cloud Run"
  type        = map(string)
  default     = {}
}

variable "allow_backend_unauthenticated" {
  description = "Permitir invocacion publica al backend en etapa inicial"
  type        = bool
  default     = true
}

variable "allow_frontend_unauthenticated" {
  description = "Permitir invocacion publica al frontend"
  type        = bool
  default     = true
}
