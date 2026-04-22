output "global_ip_address" {
  value = google_compute_global_address.this.address
}

output "backend_service_id" {
  value = google_compute_backend_service.frontend.id
}

output "url_map_id" {
  value = google_compute_url_map.this.id
}

output "https_forwarding_rule_name" {
  value = var.enable_https ? google_compute_global_forwarding_rule.https[0].name : null
}

output "managed_certificate_name" {
  value = var.enable_https && length(var.managed_certificate_domains) > 0 ? google_compute_managed_ssl_certificate.this[0].name : null
}

output "self_signed_certificate_name" {
  value = var.enable_https && length(var.managed_certificate_domains) == 0 ? google_compute_ssl_certificate.self_signed[0].name : null
}
