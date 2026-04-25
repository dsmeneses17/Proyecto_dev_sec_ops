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

  rotate_secret_source_dir = "${path.module}/functions/rotate_secret"
}

data "archive_file" "rotate_secret_zip" {
  type        = "zip"
  source_dir  = local.rotate_secret_source_dir
  output_path = "${path.module}/.terraform/rotate-secret.zip"
}

resource "google_storage_bucket_object" "rotate_secret_source" {
  name   = "functions/rotate-secret-${data.archive_file.rotate_secret_zip.output_md5}.zip"
  bucket = local.images_bucket_name
  source = data.archive_file.rotate_secret_zip.output_path

  depends_on = [module.storage]
}

resource "google_project_service" "required" {
  for_each = toset([
    "compute.googleapis.com",
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "dns.googleapis.com",
    "cloudfunctions.googleapis.com",
    "eventarc.googleapis.com",
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

import {
  for_each = var.create_cloud_run ? toset(["backend-sa"]) : toset([])

  to = google_service_account.backend[0]
  id = "projects/${var.project_id}/serviceAccounts/lm-be-${var.environment}@${var.project_id}.iam.gserviceaccount.com"
}

import {
  for_each = var.create_cloud_run ? toset(["frontend-sa"]) : toset([])

  to = google_service_account.frontend[0]
  id = "projects/${var.project_id}/serviceAccounts/lm-fe-${var.environment}@${var.project_id}.iam.gserviceaccount.com"
}

resource "google_cloudfunctions2_function" "rotate_secret" {
  name     = "rotate-secret"
  project  = var.project_id
  location = var.region

  build_config {
    runtime     = "python311"
    entry_point = "rotate_secret"
    source {
      storage_source {
        bucket = local.images_bucket_name
        object = google_storage_bucket_object.rotate_secret_source.name
      }
    }
  }

  service_config {
    available_memory      = "256M"
    max_instance_count    = 10
    timeout_seconds       = 60
    ingress_settings      = "ALLOW_ALL"
    service_account_email = "${var.project_id}@appspot.gserviceaccount.com"

    environment_variables = {
      PROJECT_ID              = var.project_id
      REGION                  = var.region
      JWT_SECRET_NAME         = var.jwt_secret_name
      DB_SECRET_NAME          = var.db_password_secret_name
      CLOUD_SQL_INSTANCE      = var.create_cloud_sql ? module.cloud_sql[0].instance_name : ""
      CLOUD_SQL_DB_USER       = var.db_user
      BACKEND_SERVICE_NAME    = var.create_cloud_run ? module.backend[0].name : ""
      FRONTEND_SERVICE_NAME   = var.create_cloud_run ? module.frontend[0].name : ""
      FORCE_CLOUD_RUN_REFRESH = var.create_cloud_run ? "true" : "false"
      ROTATE_DB_USER_PASSWORD = var.create_cloud_sql ? "true" : "false"
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = "projects/${var.project_id}/topics/secret-rotation-topic"
    retry_policy   = "RETRY_POLICY_DO_NOT_RETRY"
  }

  depends_on = [google_project_service.required]
}

import {
  for_each = toset(["rotate-secret-function"])

  to = google_cloudfunctions2_function.rotate_secret
  id = "projects/${var.project_id}/locations/${var.region}/functions/rotate-secret"
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
  for_each = var.create_cloud_router_nat ? toset(["nat"]) : toset([])

  to = module.vpc.google_compute_router_nat.this[0]
  id = "projects/${var.project_id}/regions/${var.region}/routers/${local.prefix}-vpc-cr/${local.prefix}-vpc-nat"
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

resource "google_project_iam_member" "rotate_secret_sa_secret_admin" {
  project = var.project_id
  role    = "roles/secretmanager.admin"
  member  = "serviceAccount:${var.project_id}@appspot.gserviceaccount.com"
}

import {
  for_each = toset(["rotate-secret-secret-admin"])

  to = google_project_iam_member.rotate_secret_sa_secret_admin
  id = "${var.project_id} roles/secretmanager.admin serviceAccount:${var.project_id}@appspot.gserviceaccount.com"
}

resource "google_project_iam_member" "rotate_secret_sa_cloudsql_admin" {
  project = var.project_id
  role    = "roles/cloudsql.admin"
  member  = "serviceAccount:${var.project_id}@appspot.gserviceaccount.com"
}

import {
  for_each = toset(["rotate-secret-cloudsql-admin"])

  to = google_project_iam_member.rotate_secret_sa_cloudsql_admin
  id = "${var.project_id} roles/cloudsql.admin serviceAccount:${var.project_id}@appspot.gserviceaccount.com"
}

resource "google_project_iam_member" "rotate_secret_sa_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${var.project_id}@appspot.gserviceaccount.com"
}

import {
  for_each = toset(["rotate-secret-run-admin"])

  to = google_project_iam_member.rotate_secret_sa_run_admin
  id = "${var.project_id} roles/run.admin serviceAccount:${var.project_id}@appspot.gserviceaccount.com"
}

resource "google_service_account_iam_member" "rotate_secret_backend_sa_user" {
  count = var.create_cloud_run ? 1 : 0

  service_account_id = google_service_account.backend[0].name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${var.project_id}@appspot.gserviceaccount.com"
}

import {
  for_each = var.create_cloud_run ? toset(["rotate-secret-backend-sa-user"]) : toset([])

  to = google_service_account_iam_member.rotate_secret_backend_sa_user[0]
  id = "projects/${var.project_id}/serviceAccounts/lm-be-${var.environment}@${var.project_id}.iam.gserviceaccount.com roles/iam.serviceAccountUser serviceAccount:${var.project_id}@appspot.gserviceaccount.com"
}

resource "google_service_account_iam_member" "rotate_secret_frontend_sa_user" {
  count = var.create_cloud_run ? 1 : 0

  service_account_id = google_service_account.frontend[0].name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${var.project_id}@appspot.gserviceaccount.com"
}

import {
  for_each = var.create_cloud_run ? toset(["rotate-secret-frontend-sa-user"]) : toset([])

  to = google_service_account_iam_member.rotate_secret_frontend_sa_user[0]
  id = "projects/${var.project_id}/serviceAccounts/lm-fe-${var.environment}@${var.project_id}.iam.gserviceaccount.com roles/iam.serviceAccountUser serviceAccount:${var.project_id}@appspot.gserviceaccount.com"
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

import {
  for_each = var.create_cloud_run ? toset(["backend-cloud-run"]) : toset([])

  to = module.backend[0].google_cloud_run_v2_service.this
  id = "projects/${var.project_id}/locations/${var.region}/services/${local.prefix}-backend"
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

import {
  for_each = var.create_cloud_run ? toset(["backend-frontend-invoker"]) : toset([])

  to = google_cloud_run_v2_service_iam_member.backend_frontend_invoker[0]
  id = "projects/${var.project_id}/locations/${var.region}/services/${local.prefix}-backend roles/run.invoker serviceAccount:${google_service_account.frontend[0].email}"
}

resource "google_project_iam_member" "backend_cloud_sql_client" {
  count = (var.create_cloud_run && var.create_cloud_sql) ? 1 : 0

  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.backend[0].email}"
}

import {
  for_each = (var.create_cloud_run && var.create_cloud_sql) ? toset(["backend-cloudsql-client"]) : toset([])

  to = google_project_iam_member.backend_cloud_sql_client[0]
  id = "${var.project_id} roles/cloudsql.client serviceAccount:${google_service_account.backend[0].email}"
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

import {
  for_each = var.create_cloud_run ? toset(["frontend-cloud-run"]) : toset([])

  to = module.frontend[0].google_cloud_run_v2_service.this
  id = "projects/${var.project_id}/locations/${var.region}/services/${local.prefix}-frontend"
}

resource "google_secret_manager_secret_iam_member" "frontend_jwt_accessor" {
  count = var.create_cloud_run ? 1 : 0

  project   = var.project_id
  secret_id = var.jwt_secret_name
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.frontend[0].email}"
}

import {
  for_each = var.create_cloud_run ? toset(["frontend-jwt-accessor"]) : toset([])

  to = google_secret_manager_secret_iam_member.frontend_jwt_accessor[0]
  id = "projects/${var.project_id}/secrets/${var.jwt_secret_name}/roles/secretmanager.secretAccessor/serviceAccount:${google_service_account.frontend[0].email}"
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
