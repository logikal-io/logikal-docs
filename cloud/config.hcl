locals {
  organization = "logikal.io"
  project = "docs"
  backend = "gcs"

  providers = {
    google = {
      version = "~> 5.9"
      region = "europe-west6"
    }
    dnsimple = {
      version = "~> 1.3"
    }
  }
}
