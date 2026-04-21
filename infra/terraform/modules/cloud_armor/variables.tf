variable "name" {
  type = string
}

variable "description" {
  type    = string
  default = "Cloud Armor policy for LiveMenu"
}

variable "rate_limit_count" {
  type    = number
  default = 100
}

variable "rate_limit_interval_sec" {
  type    = number
  default = 60
}
