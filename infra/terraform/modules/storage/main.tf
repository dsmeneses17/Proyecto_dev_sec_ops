resource "google_storage_bucket" "this" {
  name                        = var.bucket_name
  location                    = var.location
  force_destroy               = var.force_destroy
  uniform_bucket_level_access = true

  labels = var.labels

  versioning {
    enabled = var.versioning_enabled
  }

  public_access_prevention = "enforced"
}
