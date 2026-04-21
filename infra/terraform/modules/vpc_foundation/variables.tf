variable "network_name" {
  description = "Nombre de la VPC"
  type        = string
}

variable "region" {
  description = "Region principal"
  type        = string
}

variable "subnets" {
  description = "Subredes a crear con separacion por capa"
  type = map(object({
    cidr        = string
    region      = string
    description = string
  }))
}

variable "create_cloud_router_nat" {
  description = "Crear Cloud Router + Cloud NAT para egreso privado"
  type        = bool
  default     = true
}

variable "create_iap_ssh_rule" {
  description = "Crear regla de IAP para SSH administrativo"
  type        = bool
  default     = false
}

variable "iap_ssh_target_tags" {
  description = "Tags de destino para regla IAP SSH"
  type        = list(string)
  default     = []
}
