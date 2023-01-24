output "docs_workload_identity_provider" {
  description = "The full identifier of the GitHub workload identity pool provider"
  value = module.github_auth.workload_identity_provider
}

output "docs_uploader_service_account" {
  description = "The email of the Google Cloud service account for uploading documentation files"
  value = module.github_auth.service_account_emails["docs-uploader"]
}

output "docs_website_service_url_map" {
  description = "The website service URL map name to use for CDN cache invalidation"
  value = module.docs_website.website_service_url_map
}

output "docs_https_redirect_url_map" {
  description = "The HTTP to HTTPS redirection URL map name to use for CDN cache invalidation"
  value = module.docs_website.https_redirect_url_map
}

output "docs_target_bucket" {
  description = "The bucket where the documentation files should be uploaded"
  value = module.docs_website.bucket_name
}
