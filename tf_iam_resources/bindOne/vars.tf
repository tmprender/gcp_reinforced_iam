variable "project_id" {
   default = "project1"
}

variable "region" {
  default = "us-east4"
}

variable "role" {
 type = string 
 default = "roles/compute.admin"
 description = "role to bind"
 
}

variable "member" {
  type = string
  default = "serviceAccount:tf-admin@project1.iam.gserviceaccount.com"
  description = "user: or serviceAccount: to assume role"
}

