create_cloud_router_nat = true
create_cloud_dns = false
dns_domain       = ""

project_id  = "proyecto-devsecops-493813"
region      = "us-central1"
environment = "foundation-dev"

create_frontend_lb = false
create_waf_policy  = true

frontend_cloud_run_service_name = ""

enable_cdn = true

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
