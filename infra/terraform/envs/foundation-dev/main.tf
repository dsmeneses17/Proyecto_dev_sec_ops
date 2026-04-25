locals {
  prefix             = "livemenu-${var.environment}"
  root_domain        = trimsuffix(var.dns_domain, ".")
  frontend_fqdn      = "${var.frontend_subdomain}.${trimsuffix(var.dns_domain, ".")}"
  images_bucket_name = length(trimspace(var.images_bucket_name)) > 0 ? var.images_bucket_name : "${local.prefix}-images-${var.project_id}"

  backend_env_vars = merge(
    var.backend_env_vars,
    var.create_storage ? {
      STORAGE_PROVIDER = "gcs"
      GCP_PROJECT_ID   = var.project_id
      GCS_BUCKET_NAME  = local.images_bucket_name
    } : {},
    var.create_cloud_sql ? {
      DB_USER                   = var.db_user
      DB_NAME                   = var.db_name
      CLOUD_SQL_CONNECTION_NAME = module.cloud_sql[0].connection_name
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
    "cloudfunctions.googleapis.com",
    "cloudbuild.googleapis.com",
    "pubsub.googleapis.com",
    "sqladmin.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "secretmanager.googleapis.com",
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

resource "google_cloudfunctions_function" "rotate_secret" {
  count = var.manage_rotate_secret_function ? 1 : 0

  name                  = "rotate-secret"
  project               = var.project_id
  region                = var.region
  runtime               = "python311"
  available_memory_mb   = 256
  entry_point           = "rotate_secret"
  service_account_email = "${var.project_id}@appspot.gserviceaccount.com"
  ingress_settings      = "ALLOW_ALL"
  max_instances         = 3000
  timeout               = 60

  source_archive_bucket = "uploads-745023658003.us-central1.cloudfunctions.appspot.com"
  source_archive_object = "2f0f3352-3114-4813-be22-26043da06431.zip"

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = "projects/${var.project_id}/topics/secret-rotation-topic"
    failure_policy {
      retry = false
    }
  }

  labels = {
    deployment-tool = "cli-gcloud"
  }

  depends_on = [google_project_service.required]

  lifecycle {
    ignore_changes = [
      labels,
      source_archive_bucket,
      source_archive_object,
    ]
  }
}


import {
  to = google_project_service.required["cloudbuild.googleapis.com"]
  id = "${var.project_id}/cloudbuild.googleapis.com"
}

import {
  to = google_project_service.required["cloudfunctions.googleapis.com"]
  id = "${var.project_id}/cloudfunctions.googleapis.com"
}

import {
  to = google_project_service.required["pubsub.googleapis.com"]
  id = "${var.project_id}/pubsub.googleapis.com"
}

import {
  for_each = var.create_storage ? toset(["worker-sa"]) : toset([])

  to = google_service_account.worker[0]
  id = "projects/${var.project_id}/serviceAccounts/lm-worker-${var.environment}@${var.project_id}.iam.gserviceaccount.com"
}

import {
  for_each = var.create_waf_policy ? toset(["waf-policy"]) : toset([])

  to = module.waf[0].google_compute_security_policy.this
  id = "projects/${var.project_id}/global/securityPolicies/${local.prefix}-armor"
}

import {
  for_each = var.create_storage ? toset(["images-bucket"]) : toset([])

  to = module.storage[0].google_storage_bucket.this
  id = local.images_bucket_name
}

import {
  to = module.vpc.google_compute_network.this
  id = "projects/${var.project_id}/global/networks/${local.prefix}-vpc"
}

import {
  for_each = var.subnets

  to = module.vpc.google_compute_subnetwork.this[each.key]
  id = "projects/${var.project_id}/regions/${each.value.region}/subnetworks/${each.key}"
}

import {
  for_each = var.create_cloud_router_nat ? toset(["router"]) : toset([])

  to = module.vpc.google_compute_router.this[0]
  id = "projects/${var.project_id}/regions/${var.region}/routers/${local.prefix}-vpc-cr"
}

import {
  to = module.vpc.google_compute_firewall.allow_internal
  id = "projects/${var.project_id}/global/firewalls/${local.prefix}-vpc-allow-internal"
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
  secret_env_vars = {
    SECRET_KEY = {
      secret  = var.jwt_secret_name
      version = var.secret_version
    }
    DB_PASSWORD = {
      secret  = var.db_password_secret_name
      version = var.secret_version
    }
  }
  cloud_sql_instances = var.create_cloud_sql ? [module.cloud_sql[0].connection_name] : []

  depends_on = [google_project_service.required, module.cloud_sql]
}

resource "google_secret_manager_secret_iam_member" "backend_jwt_accessor" {
  count = var.create_cloud_run ? 1 : 0

  project   = var.project_id
  secret_id = var.jwt_secret_name
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.backend[0].email}"
}

resource "google_secret_manager_secret_iam_member" "backend_db_password_accessor" {
  count = (var.create_cloud_run && var.create_cloud_sql) ? 1 : 0

  project   = var.project_id
  secret_id = var.db_password_secret_name
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.backend[0].email}"
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
  ingress               = var.frontend_ingress
  allow_unauthenticated = var.allow_frontend_unauthenticated
  min_instance_count    = 0
  max_instance_count    = 3
  labels                = local.labels
  secret_env_vars = {
    SECRET_KEY = {
      secret  = var.jwt_secret_name
      version = var.secret_version
    }
  }
  env_vars = merge(
    {
      BACKEND_URL = format("%s/api/v1/", trimsuffix(module.backend[0].uri, "/"))
    },
    local.frontend_env_vars
  )

  depends_on = [google_project_service.required]
}

resource "google_secret_manager_secret_iam_member" "frontend_jwt_accessor" {
  count = var.create_cloud_run ? 1 : 0

  project   = var.project_id
  secret_id = var.jwt_secret_name
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.frontend[0].email}"
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

  region                            = var.region
  cloud_run_service_name            = var.create_cloud_run ? module.frontend[0].name : var.frontend_cloud_run_service_name
  cloud_armor_policy_id             = var.create_waf_policy ? module.waf[0].security_policy_id : null
  enable_cdn                        = var.enable_cdn
  enable_https                      = var.enable_https_lb
  enable_http_redirect              = true
  managed_certificate_domains       = var.create_cloud_dns ? [local.frontend_fqdn] : var.managed_certificate_domains
  self_signed_certificate_dns_names = [local.frontend_fqdn]
  ip_name                           = "${local.prefix}-frontend-ip"
  neg_name                          = "${local.prefix}-frontend-neg"
  backend_service_name              = "${local.prefix}-frontend-bes"
  url_map_name                      = "${local.prefix}-frontend-urlmap"
  http_proxy_name                   = "${local.prefix}-frontend-http-proxy"
  http_forwarding_rule_name         = "${local.prefix}-frontend-http-fr"
  https_proxy_name                  = "${local.prefix}-frontend-https-proxy"
  https_forwarding_rule_name        = "${local.prefix}-frontend-https-fr"

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
