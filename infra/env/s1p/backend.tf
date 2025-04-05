terraform {
  backend "gcs" {
    bucket  = "tf-state-sherlock-s1p"
    prefix  = "state"
  }
}