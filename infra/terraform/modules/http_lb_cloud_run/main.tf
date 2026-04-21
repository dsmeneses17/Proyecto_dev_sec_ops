resource "google_compute_global_address" "this" {
  name = var.ip_name
}

resource "google_compute_region_network_endpoint_group" "frontend" {
  name                  = var.neg_name
  network_endpoint_type = "SERVERLESS"
  region                = var.region

  cloud_run {
    service = var.cloud_run_service_name
  }
}

resource "google_compute_backend_service" "frontend" {
  name                  = var.backend_service_name
  protocol              = "HTTP"
  port_name             = "http"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  timeout_sec           = 30
  enable_cdn            = var.enable_cdn
  security_policy       = var.cloud_armor_policy_id

  backend {
    group = google_compute_region_network_endpoint_group.frontend.id
  }
}

resource "google_compute_url_map" "this" {
  name            = var.url_map_name
  default_service = google_compute_backend_service.frontend.id
}

resource "google_compute_target_http_proxy" "this" {
  name    = var.http_proxy_name
  url_map = google_compute_url_map.this.id
}

resource "google_compute_global_forwarding_rule" "http" {
  name                  = var.http_forwarding_rule_name
  ip_address            = google_compute_global_address.this.id
  load_balancing_scheme = "EXTERNAL_MANAGED"
  port_range            = "80"
  target                = google_compute_target_http_proxy.this.id
}

resource "google_compute_managed_ssl_certificate" "this" {
  count = var.enable_https ? 1 : 0

  name = "${var.ip_name}-managed-cert"

  managed {
    domains = var.managed_certificate_domains
  }
}

resource "google_compute_target_https_proxy" "this" {
  count = var.enable_https ? 1 : 0

  name             = coalesce(var.https_proxy_name, "${var.http_proxy_name}-https")
  url_map          = google_compute_url_map.this.id
  ssl_certificates = [google_compute_managed_ssl_certificate.this[0].id]
}

resource "google_compute_global_forwarding_rule" "https" {
  count = var.enable_https ? 1 : 0

  name                  = coalesce(var.https_forwarding_rule_name, "${var.http_forwarding_rule_name}-https")
  ip_address            = google_compute_global_address.this.id
  load_balancing_scheme = "EXTERNAL_MANAGED"
  port_range            = "443"
  target                = google_compute_target_https_proxy.this[0].id
}
