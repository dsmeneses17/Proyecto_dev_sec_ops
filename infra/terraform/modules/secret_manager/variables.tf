variable "secrets" {
  type      = map(string)
  sensitive = true
}

variable "labels" {
  type    = map(string)
  default = {}
}
