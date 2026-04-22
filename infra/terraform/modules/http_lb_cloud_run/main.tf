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

resource "google_compute_url_map" "redirect" {
  count = var.enable_https && var.enable_http_redirect ? 1 : 0

  name = "${var.url_map_name}-redirect"

  default_url_redirect {
    https_redirect = true
    strip_query    = false
  }
}

resource "google_compute_target_http_proxy" "this" {
  count = var.enable_http_redirect ? 1 : 0

  name    = var.http_proxy_name
  url_map = var.enable_https ? google_compute_url_map.redirect[0].id : google_compute_url_map.this.id
}

resource "google_compute_global_forwarding_rule" "http" {
  count = var.enable_http_redirect ? 1 : 0

  name                  = var.http_forwarding_rule_name
  ip_address            = google_compute_global_address.this.id
  load_balancing_scheme = "EXTERNAL_MANAGED"
  port_range            = "80"
  target                = google_compute_target_http_proxy.this[0].id
}

resource "tls_private_key" "self_signed" {
  count     = var.enable_https && length(var.managed_certificate_domains) == 0 ? 1 : 0
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "tls_self_signed_cert" "this" {
  count = var.enable_https && length(var.managed_certificate_domains) == 0 ? 1 : 0

  private_key_pem = tls_private_key.self_signed[0].private_key_pem

  subject {
    common_name  = length(var.self_signed_certificate_dns_names) > 0 ? var.self_signed_certificate_dns_names[0] : var.ip_name
    organization = "LiveMenu"
  }

  validity_period_hours = 8760

  allowed_uses = [
    "key_encipherment",
    "digital_signature",
    "server_auth",
  ]

  dns_names    = var.self_signed_certificate_dns_names
  ip_addresses = [google_compute_global_address.this.address]
}

resource "google_compute_ssl_certificate" "self_signed" {
  count = var.enable_https && length(var.managed_certificate_domains) == 0 ? 1 : 0

  name        = "${var.ip_name}-self-signed-cert"
  private_key = tls_private_key.self_signed[0].private_key_pem
  certificate = tls_self_signed_cert.this[0].cert_pem
}

resource "google_compute_managed_ssl_certificate" "this" {
  count = var.enable_https && length(var.managed_certificate_domains) > 0 ? 1 : 0

  name = "${var.ip_name}-managed-cert"

  managed {
    domains = var.managed_certificate_domains
  }
}

resource "google_compute_target_https_proxy" "this" {
  count = var.enable_https ? 1 : 0

  name             = coalesce(var.https_proxy_name, "${var.http_proxy_name}-https")
  url_map          = google_compute_url_map.this.id
  ssl_certificates = length(var.managed_certificate_domains) > 0 ? [google_compute_managed_ssl_certificate.this[0].id] : [google_compute_ssl_certificate.self_signed[0].id]
}

resource "google_compute_global_forwarding_rule" "https" {
  count = var.enable_https ? 1 : 0

  name                  = coalesce(var.https_forwarding_rule_name, "${var.http_forwarding_rule_name}-https")
  ip_address            = google_compute_global_address.this.id
  load_balancing_scheme = "EXTERNAL_MANAGED"
  port_range            = "443"
  target                = google_compute_target_https_proxy.this[0].id
}
