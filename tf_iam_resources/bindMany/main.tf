resource "google_project_iam_binding" "iam_binding" {
  project = "your-project-id"
  role    = "roles/editor"

  members = [
    "user:jane@example.com",
  ]

  condition {
    title       = "expires_after_2020_12_31"
    description = "Expiring at midnight of 2020-12-31"
    expression  = "request.time < timestamp(\"2021-01-01T00:00:00Z\")"
  }
}