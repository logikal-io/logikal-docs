locals {
  organization = "logikal.io"
  project = "docs"
  backend = "gcs"

  providers = {
    google = {
      version = "~> 6.19"
      region = "europe-west6"
    }
    dnsimple = {
      version = "~> 1.8"
    }
  }
}
