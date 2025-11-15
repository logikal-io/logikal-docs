output "workload_identity_provider" {
  value = module.github_auth.workload_identity_provider
}

output "service_account_email" {
  value = module.github_auth.service_account_emails["docs-publisher"]
}

output "bucket_name" {
  value = module.docs_website.bucket_name
}

output "url_map_name" {
  value = module.docs_website.url_map_name
}

output "http_to_https_url_map_name" {
  value = module.docs_website.http_to_https_url_map_name
}
