locals {
  prefix        = "livemenu-${var.environment}"
  root_domain   = trimsuffix(var.dns_domain, ".")
  frontend_fqdn = "${var.frontend_subdomain}.${trimsuffix(var.dns_domain, ".")}"
  images_bucket_name = length(trimspace(var.images_bucket_name)) > 0 ? var.images_bucket_name : "${local.prefix}-images-${var.project_id}"

  backend_env_vars = merge(
    var.backend_env_vars,
    var.create_storage ? {
      STORAGE_PROVIDER = "gcs"
      GCP_PROJECT_ID   = var.project_id
      GCS_BUCKET_NAME  = local.images_bucket_name
    } : {},
    var.create_cloud_sql ? {
      DATABASE_URL = format(
        "postgresql+psycopg2://%s:%s@/%s?host=/cloudsql/%s",
        var.db_user,
        var.db_password,
        var.db_name,
        module.cloud_sql[0].connection_name
      )
    } : {}
  )

  frontend_env_vars = merge(
    var.frontend_env_vars,
    var.create_storage ? {
      STORAGE_PROVIDER = "gcs"
      GCP_PROJECT_ID   = var.project_id
      GCS_BUCKET_NAME  = local.images_bucket_name
    } : {}
  )

  labels = {
    app = "livemenu"
    env = var.environment
  }
}

resource "google_project_service" "required" {
  for_each = toset([
    "compute.googleapis.com",
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "dns.googleapis.com",
    "sqladmin.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "storage.googleapis.com"
  ])

  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}

resource "google_dns_managed_zone" "public" {
  count = var.create_cloud_dns ? 1 : 0

  name        = var.dns_zone_name
  dns_name    = "${local.root_domain}."
  description = "Public zone for LiveMenu frontend"

  visibility = "public"
}

resource "google_service_account" "backend" {
  count = var.create_cloud_run ? 1 : 0

  account_id   = "lm-be-${var.environment}"
  display_name = "LiveMenu Backend ${var.environment}"
}

resource "google_service_account" "frontend" {
  count = var.create_cloud_run ? 1 : 0

  account_id   = "lm-fe-${var.environment}"
  display_name = "LiveMenu Frontend ${var.environment}"
}

resource "google_service_account" "worker" {
  count = var.create_storage ? 1 : 0

  account_id   = "lm-worker-${var.environment}"
  display_name = "LiveMenu Worker ${var.environment}"
}

module "storage" {
  count  = var.create_storage ? 1 : 0
  source = "../../modules/storage"

  bucket_name        = local.images_bucket_name
  location           = var.region
  versioning_enabled = true
  labels             = local.labels

  depends_on = [google_project_service.required]
}

module "backend" {
  count  = var.create_cloud_run ? 1 : 0
  source = "../../modules/cloud_run_service"

  name                  = "${local.prefix}-backend"
  region                = var.region
  image                 = var.backend_image
  service_account       = google_service_account.backend[0].email
  container_port        = var.backend_container_port
  ingress               = var.backend_ingress
  allow_unauthenticated = var.allow_backend_unauthenticated
  min_instance_count    = 0
  max_instance_count    = 3
  labels                = local.labels
  env_vars              = local.backend_env_vars
  cloud_sql_instances   = var.create_cloud_sql ? [module.cloud_sql[0].connection_name] : []

  depends_on = [google_project_service.required, module.cloud_sql]
}

resource "google_cloud_run_v2_service_iam_member" "backend_frontend_invoker" {
  count = var.create_cloud_run ? 1 : 0

  project  = var.project_id
  location = var.region
  name     = module.backend[0].name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.frontend[0].email}"
}

resource "google_project_iam_member" "backend_cloud_sql_client" {
  count = (var.create_cloud_run && var.create_cloud_sql) ? 1 : 0

  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.backend[0].email}"
}

resource "google_storage_bucket_iam_member" "backend_object_viewer" {
  count = (var.create_storage && var.create_cloud_run) ? 1 : 0

  bucket = module.storage[0].bucket_name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.backend[0].email}"
}

resource "google_storage_bucket_iam_member" "frontend_object_admin" {
  count = (var.create_storage && var.create_cloud_run) ? 1 : 0

  bucket = module.storage[0].bucket_name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.frontend[0].email}"
}

resource "google_storage_bucket_iam_member" "worker_object_admin" {
  count = var.create_storage ? 1 : 0

  bucket = module.storage[0].bucket_name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.worker[0].email}"
}

module "frontend" {
  count  = var.create_cloud_run ? 1 : 0
  source = "../../modules/cloud_run_service"

  name                  = "${local.prefix}-frontend"
  region                = var.region
  image                 = var.frontend_image
  service_account       = google_service_account.frontend[0].email
  container_port        = var.frontend_container_port
  allow_unauthenticated = var.allow_frontend_unauthenticated
  min_instance_count    = 0
  max_instance_count    = 3
  labels                = local.labels
  env_vars = merge(
    {
      BACKEND_URL = format("%s/api/v1/", trimsuffix(module.backend[0].uri, "/"))
    },
    local.frontend_env_vars
  )

  depends_on = [google_project_service.required]
}

module "vpc" {
  source = "../../modules/vpc_foundation"

  network_name            = "${local.prefix}-vpc"
  region                  = var.region
  subnets                 = var.subnets
  create_cloud_router_nat = var.create_cloud_router_nat

  depends_on = [google_project_service.required]
}

module "cloud_sql" {
  count  = var.create_cloud_sql ? 1 : 0
  source = "../../modules/cloud_sql"

  instance_name       = "${local.prefix}-pg"
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

module "waf" {
  count  = var.create_waf_policy ? 1 : 0
  source = "../../modules/cloud_armor"

  name                    = "${local.prefix}-armor"
  description             = "Cloud Armor policy for ${local.prefix}"
  rate_limit_count        = var.rate_limit_count
  rate_limit_interval_sec = var.rate_limit_interval_sec

  depends_on = [google_project_service.required]
}

module "frontend_lb" {
  count  = var.create_frontend_lb ? 1 : 0
  source = "../../modules/http_lb_cloud_run"

  region                      = var.region
  cloud_run_service_name      = var.create_cloud_run ? module.frontend[0].name : var.frontend_cloud_run_service_name
  cloud_armor_policy_id       = var.create_waf_policy ? module.waf[0].security_policy_id : null
  enable_cdn                  = var.enable_cdn
  enable_https                = var.enable_https_lb
  managed_certificate_domains = var.create_cloud_dns ? [local.frontend_fqdn] : var.managed_certificate_domains
  ip_name                     = "${local.prefix}-frontend-ip"
  neg_name                    = "${local.prefix}-frontend-neg"
  backend_service_name        = "${local.prefix}-frontend-bes"
  url_map_name                = "${local.prefix}-frontend-urlmap"
  http_proxy_name             = "${local.prefix}-frontend-http-proxy"
  http_forwarding_rule_name   = "${local.prefix}-frontend-http-fr"
  https_proxy_name            = "${local.prefix}-frontend-https-proxy"
  https_forwarding_rule_name  = "${local.prefix}-frontend-https-fr"

  depends_on = [google_project_service.required, module.frontend, google_dns_managed_zone.public]
}

resource "google_dns_record_set" "frontend_a" {
  count = (var.create_cloud_dns && var.create_frontend_lb) ? 1 : 0

  name         = "${local.frontend_fqdn}."
  managed_zone = google_dns_managed_zone.public[0].name
  type         = "A"
  ttl          = 300
  rrdatas      = [module.frontend_lb[0].global_ip_address]
}
