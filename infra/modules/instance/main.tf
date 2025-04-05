data "terraform_remote_state" "base" {
  backend = "gcs"
  config = {
    bucket  = var.base_state_bucket
    prefix  = "state"
  }
}