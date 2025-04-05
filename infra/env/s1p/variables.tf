variable "project_id" {
  default = "just-escape-246007"
  type    = string
}

variable "gcp_region" {
  default = "europe-west1"
  type    = string
}

variable "namespace" {
  default = "s1p"
  type    = string
}

variable "base_state_bucket" {
  default = "tf-state-sherlock-base"
  type = string
}