locals {
  name_prefix = "livemenu-${var.environment}"
  labels = {
    app = "livemenu"
    env = var.environment
  }
}

resource "google_project_service" "required" {
  for_each = toset(concat(
    [
      "run.googleapis.com",
      "artifactregistry.googleapis.com",
      "cloudresourcemanager.googleapis.com"
    ],
    var.create_cloud_sql ? ["sqladmin.googleapis.com"] : [],
    var.create_secret_manager ? ["secretmanager.googleapis.com"] : [],
    var.create_cloud_armor ? ["compute.googleapis.com"] : []
  ))

  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}

resource "google_service_account" "backend" {
  account_id   = "livemenu-backend-${var.environment}"
  display_name = "LiveMenu Backend ${var.environment}"
}

resource "google_service_account" "frontend" {
  account_id   = "livemenu-frontend-${var.environment}"
  display_name = "LiveMenu Frontend ${var.environment}"
}

module "storage" {
  count  = var.create_storage ? 1 : 0
  source = "../../modules/storage"

  bucket_name        = "${local.name_prefix}-images-${var.project_id}"
  location           = var.region
  versioning_enabled = true
  labels             = local.labels

  depends_on = [google_project_service.required]
}

module "cloud_sql" {
  count  = var.create_cloud_sql ? 1 : 0
  source = "../../modules/cloud_sql"

  instance_name       = "${local.name_prefix}-pg"
  region              = var.region
  tier                = var.db_tier
  availability_type   = "REGIONAL"
  retained_backups    = 15
  deletion_protection = true
  database_name       = var.db_name
  database_user       = var.db_user
  database_password   = var.db_password

  depends_on = [google_project_service.required]
}

module "secrets" {
  count  = var.create_secret_manager ? 1 : 0
  source = "../../modules/secret_manager"

  secrets = {
    "${local.name_prefix}-db-password" = var.db_password
    "${local.name_prefix}-jwt-secret"  = var.jwt_secret
  }

  labels = local.labels

  depends_on = [google_project_service.required]
}

module "cloud_armor" {
  count  = var.create_cloud_armor ? 1 : 0
  source = "../../modules/cloud_armor"

  name        = "${local.name_prefix}-armor"
  description = "WAF policy para LiveMenu ${var.environment}"

  depends_on = [google_project_service.required]
}

module "backend" {
  source = "../../modules/cloud_run_service"

  name                  = "${local.name_prefix}-backend"
  region                = var.region
  image                 = var.backend_image
  service_account       = google_service_account.backend.email
  container_port        = 5000
  allow_unauthenticated = var.allow_backend_unauthenticated
  min_instance_count    = 0
  max_instance_count    = 5
  labels                = local.labels

  env_vars = merge(
    {
      ENVIRONMENT = var.environment
    },
    var.create_storage ? {
      GCS_BUCKET_NAME = module.storage[0].bucket_name
    } : {},
    var.create_cloud_sql ? {
      CLOUD_SQL_CONNECTION_NAME = module.cloud_sql[0].connection_name
    } : {},
    var.backend_env_vars
  )

  depends_on = [google_project_service.required]
}

module "frontend" {
  source = "../../modules/cloud_run_service"

  name                  = "${local.name_prefix}-frontend"
  region                = var.region
  image                 = var.frontend_image
  service_account       = google_service_account.frontend.email
  container_port        = 8000
  allow_unauthenticated = var.allow_frontend_unauthenticated
  min_instance_count    = 0
  max_instance_count    = 3
  labels                = local.labels

  env_vars = merge(
    {
      ENVIRONMENT = var.environment
    },
    var.frontend_env_vars
  )

  depends_on = [google_project_service.required]
}
