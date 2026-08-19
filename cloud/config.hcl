locals {
  state_backend = "gcs"
  organization = "logikal.io"
  project = "docs"

  providers = {
    google = {
      version = "~> 7.45"
      region = "europe-west6"
    }
  }

  modules = {
    "github.com/logikal-io/terraform-modules" = "v5.4.0"
  }
}
