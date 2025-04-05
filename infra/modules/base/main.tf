resource "google_artifact_registry_repository" "sherlock" {
  location      = var.gcp_region
  repository_id = "sherlock"
  format        = "DOCKER"
}