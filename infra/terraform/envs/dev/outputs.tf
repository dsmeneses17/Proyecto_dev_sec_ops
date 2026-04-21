output "frontend_url" {
  value = module.frontend.uri
}

output "backend_url" {
  value = module.backend.uri
}

output "images_bucket" {
  value = var.create_storage ? module.storage[0].bucket_name : null
}

output "cloud_sql_connection_name" {
  value = var.create_cloud_sql ? module.cloud_sql[0].connection_name : null
}

output "cloud_armor_policy" {
  value = var.create_cloud_armor ? module.cloud_armor[0].security_policy_name : null
}
