variable "project_id" {
  type = string
  default = "project1"
}
variable "region" {
  type = string
  default = "us-east4"
}

variable "role_id" {
  type = string
  default = "working_role"

  description = "Role ID - cannot be re-used within 30 days if deleted"
}

variable "permissions" {
  type = list(string)
  default = ["compute.instances.get", "iam.roles.get", "iam.roles.list", "storage.buckets.list", "storage.buckets.get", "storage.objects.create"]

  description = "IAM permissions for the role"
}

