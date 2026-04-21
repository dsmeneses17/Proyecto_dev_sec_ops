resource "google_compute_network" "this" {
  name                    = var.network_name
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
}

resource "google_compute_subnetwork" "this" {
  for_each = var.subnets

  name                     = each.key
  ip_cidr_range            = each.value.cidr
  region                   = each.value.region
  network                  = google_compute_network.this.id
  description              = each.value.description
  private_ip_google_access = true
}

resource "google_compute_router" "this" {
  count = var.create_cloud_router_nat ? 1 : 0

  name    = "${var.network_name}-cr"
  region  = var.region
  network = google_compute_network.this.id
}

resource "google_compute_router_nat" "this" {
  count = var.create_cloud_router_nat ? 1 : 0

  name                               = "${var.network_name}-nat"
  router                             = google_compute_router.this[0].name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

resource "google_compute_firewall" "allow_internal" {
  name    = "${var.network_name}-allow-internal"
  network = google_compute_network.this.name

  direction = "INGRESS"
  priority  = 1000

  source_ranges = [for subnet in var.subnets : subnet.cidr]

  allow {
    protocol = "tcp"
  }

  allow {
    protocol = "udp"
  }

  allow {
    protocol = "icmp"
  }
}

resource "google_compute_firewall" "allow_iap_ssh" {
  count = var.create_iap_ssh_rule ? 1 : 0

  name    = "${var.network_name}-allow-iap-ssh"
  network = google_compute_network.this.name

  direction = "INGRESS"
  priority  = 1100

  source_ranges = ["35.235.240.0/20"]

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  target_tags = var.iap_ssh_target_tags
}
