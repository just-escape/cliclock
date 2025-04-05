resource "google_project_service" "apis" {
  for_each = toset([
    "logging.googleapis.com",
    "run.googleapis.com",
    "secretmanager.googleapis.com",
    "sqladmin.googleapis.com",
  ])

  service            = each.value
  disable_on_destroy = false // Don't disable the service when the Terraform resource is destroyed
}

resource "google_artifact_registry_repository" "sherlock" {
  location      = var.gcp_region
  repository_id = "sherlock"
  format        = "DOCKER"
}

resource "google_secret_manager_secret" "backoffice_db_password" {
  secret_id = "backoffice_db_password"

  replication {
    auto {}
  }
}