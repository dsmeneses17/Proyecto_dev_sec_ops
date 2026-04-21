output "network_name" {
  value = google_compute_network.this.name
}

output "network_self_link" {
  value = google_compute_network.this.self_link
}

output "subnet_names" {
  value = [for subnet in google_compute_subnetwork.this : subnet.name]
}

output "subnet_self_links" {
  value = { for k, v in google_compute_subnetwork.this : k => v.self_link }
}
