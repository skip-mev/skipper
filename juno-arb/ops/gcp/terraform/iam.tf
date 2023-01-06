resource "google_service_account" "default" {
  account_id   = "${var.instance_name}-sa"
  display_name = "Service Account"
}

resource "google_project_iam_binding" "logs-writer-iam" {
  role    = "roles/logging.logWriter"
  project = var.project

  members = [
    "serviceAccount:${google_service_account.default.email}",
  ]
}

resource "google_project_iam_binding" "metrics-writer-iam" {
  role    = "roles/monitoring.metricWriter"
  project = var.project

  members = [
    "serviceAccount:${google_service_account.default.email}",
  ]
}