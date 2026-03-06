locals {
  state_backend = "gcs"
  organization = "logikal.io"
  project = "docs"

  providers = {
    google = {
      version = "~> 7.22"
      region = "europe-west6"
    }
  }

  modules = {
    "github.com/logikal-io/terraform-modules" = "v4.0.1"
  }
}
