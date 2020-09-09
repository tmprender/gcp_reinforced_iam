resource "null_resource" "call_iam_writer" {
  provisioner "local-exec" {
    command = "../trigger-writer.sh $FUNCTION $DATA $CF_REGION"
    environment = {
        FUNCTION = "binding_record_keeper"
        DATA = jsonencode({"action"="ADD", "role"=var.role, "members"=[var.member]})
        CF_REGION = var.region
    }
  }

  provisioner "local-exec" {
    when = destroy
    command = "../trigger-writer.sh $FUNCTION $DATA $CF_REGION"
    environment = {
        FUNCTION = "binding_record_keeper"
        DATA = jsonencode({"action"="REMOVE", "role"=var.role, "members"=[var.member]})
        CF_REGION = var.region
    }
  }
}

resource "google_project_iam_member" "member_binding" {
  project = var.project_id
  role = var.role

  member = var.member

  depends_on = [null_resource.call_iam_writer]
}
