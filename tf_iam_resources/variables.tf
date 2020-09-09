variable "project_id" {
  type = string
  default = "project1"
}

variable "region" {
  type = string
  default = "us-east4"
  description = "region - use multiple region vars if needed"

}

variable "role_id" {
  type = string
  default = "iam_role_enforcer"
  description = "role name/id"
}

variable "permissions" {
  type = list(string)
  default = ["iam.roles.delete", "iam.roles.create", "storage.buckets.get", "storage.objects.get", "storage.objects.create", "storage.objects.delete"]
  description = "iam permissions for the custom role"
}  

variable "account_id" {
  type = string
  default = "iam-role-enforcer"
  description = "Service Account ID"

}


