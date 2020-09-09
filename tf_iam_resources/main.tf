provider "google" {
  credentials = file("../creds/your-cred-file.json")
  project = var.project_id
  region = var.region
}

module "customRole" {
  source = "./customRole"

  role_id     = var.role_id
  permissions = var.permissions

}

module "serviceAccount" {
  source = "./serviceAccount"
  
  account_id = var.account_id

}

module "binding" {
  source = "./bindOne"

  role = module.customRole.name
  member = join("", ["serviceAccount:", module.serviceAccount.email])
}
