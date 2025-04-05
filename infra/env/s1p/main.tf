terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.gcp_region
}

module "instance" {
  namespace  = var.namespace
  project_id = var.project_id
  gcp_region = var.gcp_region
  base_state_bucket = var.base_state_bucket
  source     = "../../modules/instance"
}
