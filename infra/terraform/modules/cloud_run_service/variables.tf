variable "name" {
  type = string
}

variable "region" {
  type = string
}

variable "image" {
  type = string
}

variable "service_account" {
  type = string
}

variable "container_port" {
  type    = number
  default = 8080
}

variable "min_instance_count" {
  type    = number
  default = 0
}

variable "max_instance_count" {
  type    = number
  default = 5
}

variable "ingress" {
  type    = string
  default = "INGRESS_TRAFFIC_ALL"
}

variable "allow_unauthenticated" {
  type    = bool
  default = false
}

variable "env_vars" {
  type    = map(string)
  default = {}
}

variable "labels" {
  type    = map(string)
  default = {}
}

variable "cloud_sql_instances" {
  description = "Cloud SQL connection names to mount through the Cloud SQL connector"
  type        = list(string)
  default     = []
}
