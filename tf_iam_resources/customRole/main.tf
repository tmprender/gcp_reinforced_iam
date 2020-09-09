# null resource to trigger record keeping before resource is created
resource "null_resource" "record_keeper_create" {

  provisioner "local-exec" {
    command = "../trigger-writer.sh $FUNCTION $DATA $CF_REGION"
    environment = {
        FUNCTION = "role_record_keeper"
        DATA = jsonencode({"action"="CREATE", "role_name"=local.full_role_name, "permissions"=var.permissions})
        CF_REGION = var.region
    }
  }
}

# null resource and trigger record keeping before resource is deleted
resource "null_resource" "record_keeper_delete" {
  triggers = {
    role_id = google_project_iam_custom_role.custom_role.role_id
  } 
  provisioner "local-exec" {
    when = destroy
    command = "../trigger-writer.sh $FUNCTION $DATA $CF_REGION"
    environment = {
        FUNCTION = "role_record_keeper"
        DATA = jsonencode({"action"="DELETE", "role_name"=local.full_role_name, "permissions"=var.permissions})
        CF_REGION = var.region
    }
  }
}

# null resource and trigger record keeping for when role is updated
resource "null_resource" "record_keeper_update" {
    triggers = {
      permission_update = "${join(",", var.permissions)}"
    }
    provisioner "local-exec" {
      command = "../trigger-writer.sh $FUNCTION $DATA $CF_REGION"
      environment = {
          FUNCTION = "role_record_keeper"
          DATA = jsonencode({"action"="UPDATE", "role_name"=local.full_role_name, "permissions"=var.permissions})
          CF_REGION = var.region
      }
    }

}

# define the role
resource "google_project_iam_custom_role" "custom_role" {
  project     = var.project_id
  role_id     = var.role_id
  title       = var.role_id
  permissions = var.permissions

  depends_on = [null_resource.record_keeper_create, null_resource.record_keeper_update]
}

locals {
  full_role_name = join("", ["projects/", var.project_id, "/roles/", var.role_id])
}
