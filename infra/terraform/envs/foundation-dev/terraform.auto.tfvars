project_id  = "proyecto-devsecops-493813"
region      = "us-central1"
environment = "foundation-dev"

# Fase 2: Cloud Run + LB frontend
create_cloud_run   = true
create_frontend_lb = true
create_waf_policy  = true
create_storage     = true

images_bucket_name = "livemenu-foundation-dev-images-proyecto-devsecops-493813"

# Solo se usa si create_cloud_run=false
frontend_cloud_run_service_name = ""

frontend_image = "us-central1-docker.pkg.dev/proyecto-devsecops-493813/cloud-run-source-deploy/livemenu-foundation-dev-frontend@sha256:67201c18d74f50f6493843229c21a86922008b9e44f5dfe5d8427618e14ba0b2"
backend_image  = "us-central1-docker.pkg.dev/proyecto-devsecops-493813/cloud-run-source-deploy/livemenu-foundation-dev-backend@sha256:18d8858f96ec5f27b8ec49c4fded6b791e3ed4274f0ad6ff7fe3cbc67bb21566"

allow_frontend_unauthenticated = true
allow_backend_unauthenticated  = false
frontend_ingress               = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"
backend_ingress                = "INGRESS_TRAFFIC_ALL"

backend_env_vars = {}

jwt_secret_name         = "jwt-secret"
db_password_secret_name = "db-password"
secret_version          = "latest"

frontend_env_vars = {
  ENFORCE_HTTPS_REDIRECT = "true"
  SESSION_COOKIE_SECURE  = "true"
}

enable_cdn         = true
enable_https_lb    = true
create_cloud_dns   = false
dns_zone_name      = "livemenu-public-zone"
dns_domain         = "livemenudevsecops.com"
frontend_subdomain = "app"

rate_limit_count        = 100
rate_limit_interval_sec = 60

subnets = {
  "livemenu-foundation-dev-snet-ingress" = {
    cidr        = "10.10.10.0/24"
    region      = "us-central1"
    description = "Subnet de ingreso y componentes de borde"
  }

  "livemenu-foundation-dev-snet-app" = {
    cidr        = "10.10.20.0/24"
    region      = "us-central1"
    description = "Subnet para componentes de aplicacion"
  }

  "livemenu-foundation-dev-snet-data" = {
    cidr        = "10.10.30.0/24"
    region      = "us-central1"
    description = "Subnet para capa de datos"
  }

  "livemenu-foundation-dev-snet-mgmt" = {
    cidr        = "10.10.40.0/24"
    region      = "us-central1"
    description = "Subnet para operaciones y gestion"
  }

  "livemenu-foundation-dev-snet-serverless-connector" = {
    cidr        = "10.10.50.0/28"
    region      = "us-central1"
    description = "Reserva para Serverless VPC Access connector"
  }
}

create_cloud_router_nat = true

# Fase 3: Cloud SQL
create_cloud_sql = true
db_tier          = "db-f1-micro"
db_name          = "livemenu"
db_user          = "livemenu_user"
