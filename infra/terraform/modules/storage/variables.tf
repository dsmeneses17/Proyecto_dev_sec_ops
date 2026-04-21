variable "bucket_name" {
  type = string
}

variable "location" {
  type = string
}

variable "versioning_enabled" {
  type    = bool
  default = true
}

variable "force_destroy" {
  type    = bool
  default = false
}

variable "labels" {
  type    = map(string)
  default = {}
}
