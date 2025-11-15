locals {
  state_backend = "gcs"
  organization = "logikal.io"
  project = "docs"

  providers = {
    google = {
      version = "~> 7.11"
      region = "europe-west6"
    }
  }

  modules = {
    "github.com/logikal-io/terraform-modules" = "v2.0.0"
  }
}
