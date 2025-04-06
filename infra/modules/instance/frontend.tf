resource "google_cloud_run_v2_service" "frontend" {
  name     = "${var.namespace}-frontend"
  location = var.gcp_region

  template {
    containers {
      image = "${var.gcp_region}-docker.pkg.dev/${var.project_id}/${data.terraform_remote_state.base.outputs.gar_name}/frontend:v1.0.4"

      resources {
        limits = {
          "cpu" = "1"
          "memory" = "512Mi"
        }
        startup_cpu_boost = true
      }

      env {
        name = "BASE_URL"
        value = "https://${var.namespace}-backoffice-${data.google_project.project.number}.${var.gcp_region}.run.app"
      }
      env {
        name = "BASE_URL_UI"
        value = "https://${var.namespace}-frontend-${data.google_project.project.number}.${var.gcp_region}.run.app"
      }
      env {
        name = "BASE_URL_WS"
        value = "wss://sherlock.justescape.fr:3130"
      }
      env {
        name = "BASE_URL_WS_SUBSCRIBE"
        value = "https://sherlock.justescape.fr:3130"
      }
    }
  }
}

resource "google_cloud_run_service_iam_member" "frontend_public_access" {
  member  = "allUsers"
  role    = "roles/run.invoker"
  service = google_cloud_run_v2_service.frontend.id
}