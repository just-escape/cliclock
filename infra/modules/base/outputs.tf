output "gar_name" {
  value = google_artifact_registry_repository.sherlock.name
}

output "backoffice_db_password_secret_id" {
  value = google_secret_manager_secret.backoffice_db_password.id
}