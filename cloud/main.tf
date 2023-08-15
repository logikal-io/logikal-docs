locals {
  packages = [
    "logikal-docs", "pytest-logikal", "mindlab", "stormware", "pyorbs", "django-logikal",
    "logikal-utils",
  ]
}

# Needed for Stormware documentation building
resource "google_project_service" "sheets" {
  service = "sheets.googleapis.com"
}

# Documentation hosting
module "github_auth" {
  source = "github.com/logikal-io/terraform-modules//gcp/github-auth?ref=v1.10.1"

  service_account_accesses = {
    "docs-uploader" = [for package in local.packages : "logikal-io/${package}"]
  }
}

module "docs_website" {
  source = "github.com/logikal-io/terraform-modules//gcp/static-website?ref=v1.10.1"

  project_id = var.project_id
  domain = "docs.logikal.io"
  force_cache_all = true
  uploader_service_account_email = module.github_auth.service_account_emails["docs-uploader"]

  redirects = [
    for package in local.packages :
    {paths = ["/${package}", "/${package}/"], redirect = "/${package}/latest/"}
  ]
}

resource "dnsimple_zone_record" "docs_website" {
  zone_name = "logikal.io"
  name = "docs"
  value = module.docs_website.ip
  type = "A"
  ttl = 3600
}
