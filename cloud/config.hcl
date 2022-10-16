locals {
  organization = "logikal.io"
  project = "docs"
  region = "europe-west6"

  providers = {
    google = "~> 4.36"
    dnsimple = "~> 0.14"
  }
}
