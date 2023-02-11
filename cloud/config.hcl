locals {
  organization = "logikal.io"
  project = "docs"
  backend = "gcs"

  providers = {
    google = {
      version = "~> 4.52"
      region = "europe-west6"
    }
    dnsimple = {
      version = "~> 0.14"
    }
  }
}
