output "network_name" {
  value = module.vpc.network_name
}

output "subnet_names" {
  value = module.vpc.subnet_names
}

output "frontend_lb_ip" {
  value = var.create_frontend_lb ? module.frontend_lb[0].global_ip_address : null
}

output "frontend_https_url" {
  value = (var.create_frontend_lb && var.enable_https_lb) ? (
    var.create_cloud_dns ? "https://${var.frontend_subdomain}.${trimsuffix(var.dns_domain, ".")}" : (
      length(var.managed_certificate_domains) > 0 ? "https://${var.managed_certificate_domains[0]}" : null
    )
  ) : null
}

output "frontend_dns_fqdn" {
  value = (var.create_cloud_dns && var.create_frontend_lb) ? "${var.frontend_subdomain}.${trimsuffix(var.dns_domain, ".")}" : null
}

output "cloud_dns_name_servers" {
  value = var.create_cloud_dns ? google_dns_managed_zone.public[0].name_servers : []
}

output "cloud_armor_policy_name" {
  value = var.create_waf_policy ? module.waf[0].security_policy_name : null
}

output "frontend_cloud_run_url" {
  value = var.create_cloud_run ? module.frontend[0].uri : null
}

output "backend_cloud_run_url" {
  value = var.create_cloud_run ? module.backend[0].uri : null
}

output "images_bucket" {
  value = var.create_storage ? module.storage[0].bucket_name : null
}

output "worker_service_account_email" {
  value = var.create_storage ? google_service_account.worker[0].email : null
}
