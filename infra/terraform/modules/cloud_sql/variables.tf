variable "instance_name" {
  type = string
}

variable "region" {
  type = string
}

variable "database_version" {
  type    = string
  default = "POSTGRES_15"
}

variable "tier" {
  type = string
}

variable "availability_type" {
  type    = string
  default = "REGIONAL"
}

variable "backup_start_time" {
  type    = string
  default = "03:00"
}

variable "retained_backups" {
  type    = number
  default = 15
}

variable "deletion_protection" {
  type    = bool
  default = true
}

variable "database_name" {
  type = string
}

variable "database_user" {
  type = string
}

variable "database_password" {
  type      = string
  sensitive = true
}
