variable "region" {
  type = string
}

variable "cloud_run_service_name" {
  description = "Nombre del servicio Cloud Run frontend"
  type        = string
}

variable "cloud_armor_policy_id" {
  description = "ID de la politica de Cloud Armor"
  type        = string
  default     = null
}

variable "enable_cdn" {
  description = "Habilitar Cloud CDN en backend service"
  type        = bool
  default     = true
}

variable "ip_name" {
  type = string
}

variable "neg_name" {
  type = string
}

variable "backend_service_name" {
  type = string
}

variable "url_map_name" {
  type = string
}

variable "http_proxy_name" {
  type = string
}

variable "http_forwarding_rule_name" {
  type = string
}

variable "enable_http_redirect" {
  description = "Habilitar redireccion HTTP->HTTPS en el LB"
  type        = bool
  default     = true
}

variable "enable_https" {
  description = "Habilitar frontend HTTPS en el load balancer"
  type        = bool
  default     = false
}

variable "managed_certificate_domains" {
  description = "Dominios para certificado administrado de Google"
  type        = list(string)
  default     = []
}

variable "self_signed_certificate_dns_names" {
  description = "DNS names para el certificado self-signed cuando no hay certificado administrado"
  type        = list(string)
  default     = []
}

variable "https_proxy_name" {
  description = "Nombre del target HTTPS proxy"
  type        = string
  default     = null
}

variable "https_forwarding_rule_name" {
  description = "Nombre del forwarding rule HTTPS"
  type        = string
  default     = null
}
