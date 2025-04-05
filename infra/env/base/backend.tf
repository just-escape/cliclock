terraform {
  backend "gcs" {
    bucket  = "tf-state-sherlock-base"
    prefix  = "state"
  }
}