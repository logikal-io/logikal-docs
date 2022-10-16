output "workload_identity_provider" {
  description = "The full identifier of the GitHub workload identity pool provider"
  value = module.github_auth.workload_identity_provider
}

output "service_account" {
  description = "The email of the Google Cloud service account for uploading documentation files"
  value = module.github_auth.service_account_emails["docs-uploader"]
}
