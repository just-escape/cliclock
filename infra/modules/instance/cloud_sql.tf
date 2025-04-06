resource "google_sql_database_instance" "database" {
  name             = "${var.namespace}-db"
  region           = var.gcp_region
  database_version = "POSTGRES_16"

  settings {
    tier = "db-f1-micro"
    edition = "ENTERPRISE"

    backup_configuration {
      enabled  = true
      location = var.gcp_region
      backup_retention_settings {
        retained_backups = 30
        retention_unit   = "COUNT"
      }
    }

    deletion_protection_enabled  = true
  }

  deletion_protection  = true
}

resource "google_project_iam_member" "backoffice_sql_client" {
  project = var.project_id
  role = "roles/cloudsql.client"
  member = google_service_account.backoffice.member
}

resource "google_sql_database" "backoffice" {
  name     = "backoffice"
  instance = google_sql_database_instance.database.name
}

data "google_secret_manager_secret_version" "backoffice_db_password" {
  secret    = data.terraform_remote_state.base.outputs.backoffice_db_password_secret_id
  version   = "latest"
}

resource "google_sql_user" "backoffice" {
  name     = "backoffice"
  instance = google_sql_database_instance.database.name
  # Display the value with gcloud secrets versions access latest --secret portail_db_password
  password = data.google_secret_manager_secret_version.backoffice_db_password.secret_data
}

resource "google_secret_manager_secret" "db_connection_uri" {
  secret_id = "${var.namespace}-db-connection-uri"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_iam_member" "backoffice_read" {
  member             = google_service_account.backoffice.member
  role               = "roles/secretmanager.secretAccessor"
  secret_id          = google_secret_manager_secret.db_connection_uri.id
}

resource "google_secret_manager_secret_version" "db_connection_uri" {
  secret      = google_secret_manager_secret.db_connection_uri.id
  secret_data = "postgres://${google_sql_user.backoffice.name}:${data.google_secret_manager_secret_version.backoffice_db_password.secret_data}@//cloudsql/${var.project_id}:${var.gcp_region}:${google_sql_database_instance.database.name}/${google_sql_database.backoffice.name}"
}