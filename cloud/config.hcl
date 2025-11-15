locals {
  state_backend = "gcs"
  organization = "logikal.io"
  project = "docs"

  providers = {
    google = {
      version = "~> 7.10"
      region = "europe-west6"
    }
    dnsimple = {
      version = "~> 1.10"
    }
  }

  modules = {
    "github.com/logikal-io/terraform-modules" = "v2.0.0"
  }
}
