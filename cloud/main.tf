locals {
  packages = [
    "logikal-docs", "pytest-logikal", "mindlab", "stormware", "pyorbs", "django-logikal",
    "logikal-utils", "logikal-browser",
  ]
}

resource "google_project_service" "sheets" {  # needed for Stormware documentation building
  service = "sheets.googleapis.com"
}

# Documentation hosting
module "github_auth" {
  source = "github.com/logikal-io/terraform-modules//gcp/github-auth"

  github_organization = var.organization_id
  service_account_accesses = {
    "docs-publisher" = [for package in local.packages : "logikal-io/${package}"]
  }
}

module "docs_website" {
  source = "github.com/logikal-io/terraform-modules//gcp/gcs-static-site"

  project_id = var.project_id
  domain_project_id = "nucleus-${var.organization_id}"
  domain_managed_zone_name = var.organization_id
  domain = "docs.logikal.io"
  force_cache_all = true
  publisher_service_account_email = module.github_auth.service_account_emails["docs-publisher"]

  redirects = [
    for package in local.packages :
    {paths = ["/${package}", "/${package}/"], redirect = "/${package}/latest/"}
  ]
}
