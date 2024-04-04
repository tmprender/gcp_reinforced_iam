# REINFORCED IAM
Cloud-native solution for managing and strengthening IAM policies.

*Please note this work is still in progress and so is the README. 
 
## ARCHITECTURE
- Record-Keeping: Terraform triggers Cloud Function via HTTP
  
  Whenever an IAM resource is created/updated/deleted via TF, call a Cloud Function to create a record of the action.

- Remediation: LogSink triggers Cloud Function via PubSub
  
  When write calls are made to the IAM API, one of three Cloud Functions will be invoked (depending on resource type) to check that: 1) an approved IAM Admin made the request, and 2) there is a record of this request/action.

 *NOTE* - Both parts of the design are standalone. Meaning: you can deploy the remedial functions without the record-keeping architecture and vice versa. Further, you can modify the remedial functions to include more checks, or to ignore the record-keeping all together. If you choose to only deploy the remedial functions, you will need to remove the 'records_updated(arg)' check(s).

## GETTING STARTED
- Prerequisites:
 -- Terraform installed
 -- GCP Project setup + Gcloud installed
 -- Service Account (and key) for provisioning resources via Terraform
 -- Role for the Terraform Service Account above (Permissions Outlined below)

- Deploy all resources via Terraform
 -- TO-DO: write terraform for Cloud Functions, Storage, SAs, Roles, etc.

## TO-DOs:
- Implement role_record_keeper pubsub call to binding_record_keeper on delete
- upload binding_enforcer_code
- Consolidate helper functions into one library file
- Write Terraform for entire platform




 
