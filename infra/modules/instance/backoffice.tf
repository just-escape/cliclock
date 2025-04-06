locals {
  media_folder = "${path.module}/../../../media"
  media_files = fileset(local.media_folder, "**")

  media_file_map = {
    for file in local.media_files : file => {
      source      = "${local.media_folder}/${file}"
      destination = file
    }
  }
}

resource "google_cloud_run_v2_service" "backoffice" {
  name     = "${var.namespace}-backoffice"
  location = var.gcp_region

  template {
    containers {
      image = "${var.gcp_region}-docker.pkg.dev/${var.project_id}/${data.terraform_remote_state.base.outputs.gar_name}/backoffice:v1.0.6"

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      env {
        name = "CLOUDRUN_SERVICE_URL"
        value = "https://${var.namespace}-backoffice-${data.google_project.project.number}.${var.gcp_region}.run.app"
      }

      env {
        name = "DJANGO_SECRET_KEY"
        value = "*****"
      }

      volume_mounts {
        name       = "media"
        mount_path = "/app/media"
      }
      # volume_mounts {
      #   name = "cloudsql"
      #   mount_path = "/cloudsql"
      # }
    }

    volumes {
      name = "media"
      gcs {
        bucket    = google_storage_bucket.media.name
        read_only = false
      }
    }

    scaling {
      max_instance_count = 1
    }
  }
}

resource "google_cloud_run_service_iam_member" "backoffice_public_access" {
  member  = "allUsers"
  role    = "roles/run.invoker"
  service = google_cloud_run_v2_service.backoffice.id
}

resource "google_storage_bucket" "media" {
  location = var.gcp_region
  name     = "${var.namespace}-sherlock-backoffice-media"
}

resource "google_storage_bucket_object" "media_files" {
  for_each = local.media_file_map

  name   = each.value.destination
  bucket = google_storage_bucket.media.id
  source = each.value.source
}