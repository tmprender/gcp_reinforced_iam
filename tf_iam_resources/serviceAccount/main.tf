resource "null_resource" "call_iam_writer" {
  provisioner "local-exec" {
    command = "../trigger-writer.sh $FUNCTION $DATA $CF_REGION"
    environment = {
        FUNCTION = "serviceAccount_record_keeper"
        DATA = jsonencode({"action"="CREATE", "account_id"=var.account_id})
        CF_REGION = var.region
    }
  }


  provisioner "local-exec" {
    when = destroy
    command = "../trigger-writer.sh $FUNCTION $DATA $CF_REGION"
    environment = {
        FUNCTION = "serviceAccount_record_keeper"
        DATA = jsonencode({"action"="DELETE", "account_id"=var.account_id})
        CF_REGION = var.region
    }
  }
}

resource "google_service_account" "service_account" {
  project = var.project_id
  account_id = var.account_id
  display_name = var.account_id

  depends_on = [null_resource.call_iam_writer]
}

# remove this block if creating a SA with no binding
/*
resource "google_project_iam_member" "sa-binding" {
  project = var.project_id
  role = var.role
~
  member = join("", ["serviceAccount:", google_service_account.service_account.email])
  
  depends_on = [google_service_account.service_account]

}*/
