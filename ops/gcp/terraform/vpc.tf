resource "google_compute_network" "skip-mev" {
  name                    = "skip-mev"
  auto_create_subnetworks = false
  mtu                     = 1460
  project                 = var.project

}

resource "google_compute_firewall" "ssh" {
  name = "allow-ssh"
  project = var.project
  allow {
    ports    = ["22"]
    protocol = "tcp"
  }
  direction     = "INGRESS"
  network       = google_compute_network.skip-mev.id
  priority      = 1000
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["ssh"]
}