locals {
  packages = ["logikal-docs", "pytest-logikal", "mindlab", "stormware", "pyorbs"]
}

# Needed for Stormware documentation building
resource "google_project_service" "sheets" {
  service = "sheets.googleapis.com"
}

# Documentation hosting
module "docs_website" {
  source = "github.com/logikal-io/terraform-modules//gcp/static-website?ref=v1.3.0"

  domain = "docs.logikal.io"
  force_cache_all = true

  redirects = [
    for package in local.packages :
    { paths = ["/${package}", "/${package}/"], redirect = "/${package}/latest/" }
  ]
}

resource "dnsimple_zone_record" "docs_website" {
  zone_name = "logikal.io"
  name = "docs"
  value = module.docs_website.ip
  type = "A"
  ttl = 3600
}

# GitHub Actions
module "github_auth" {
  source = "github.com/logikal-io/terraform-modules//gcp/github-auth?ref=v1.3.0"

  service_account_accesses = {
    "docs-uploader" = [for package in local.packages : "logikal-io/${package}"]
  }
}

resource "google_storage_bucket_iam_member" "docs_uploader_object_admin" {
  bucket = module.docs_website.bucket_name
  role = "roles/storage.objectAdmin"
  member = "serviceAccount:${module.github_auth.service_account_emails["docs-uploader"]}"
}

resource "google_project_iam_custom_role" "bucket_metadata_reader" {
  role_id = "BucketMetadataReader"
  title = "Bucket Metadata Reader"
  permissions = ["storage.buckets.get"]
}

resource "google_storage_bucket_iam_member" "docs_uploader_bucket_metadata_reader" {
  bucket = module.docs_website.bucket_name
  role = google_project_iam_custom_role.bucket_metadata_reader.id
  member = "serviceAccount:${module.github_auth.service_account_emails["docs-uploader"]}"
}

resource "google_project_iam_custom_role" "cdn_invalidator" {
  role_id = "CDNInvalidator"
  title = "CDN Invalidator"
  permissions = ["compute.urlMaps.get", "compute.urlMaps.invalidateCache"]
}

resource "google_project_iam_member" "docs_cdn_invalidator" {
  project = var.project_id
  role = google_project_iam_custom_role.cdn_invalidator.id
  member = "serviceAccount:${module.github_auth.service_account_emails["docs-uploader"]}"
}
