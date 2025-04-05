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

module "base" {
  namespace  = var.namespace
  project_id = var.project_id
  gcp_region = var.gcp_region
  source     = "../../modules/base"
}
