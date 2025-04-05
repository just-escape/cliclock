resource "google_cloud_run_v2_service" "frontend" {
  name     = "${var.namespace}-frontend"
  location = var.gcp_region

  template {
    containers {
      image = "${var.gcp_region}-docker.pkg.dev/${var.project_id}/${data.terraform_remote_state.base.outputs.gar_name}/frontend:v1.0.0"
    }
  }
}