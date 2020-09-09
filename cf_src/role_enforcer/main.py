import base64
import json
import os
from google.cloud import storage
from googleapiclient import discovery
from datetime import datetime

storage_client = storage.Client()
bucket_name = 'your_bucket_name'
bucket = storage_client.bucket(bucket_name)
project_id = os.environ.get('GCP_PROJECT')

def check_role_event(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    print(pubsub_message)
    event = json.loads(pubsub_message)
    

    method = None ; principal = None ; info = None ; status = None ; insertId = None
    try:
        method = event['protoPayload']['methodName']
        principal = event['protoPayload']['authenticationInfo']['principalEmail']
        info = event['resource']['labels']
        status = event['protoPayload']['status']
        insertId = event['insertId']
        print(method, principal, info)
    except Exception as e:
        print(e)
        return

    if status.get('message') is "OK":
        #print("default service account created by GCP backend... did an API just get enabled??")
        # not sure if this is needed for roles --  send alert ?
        return 
    
    # approved IAM Admins
    iam_admins = ['tf-admin@project1.iam.gserviceaccount.com', 'OPTIONALLY INCLUDE OWNER ACCOUNT HERE']
 
    if principal not in iam_admins:
        print('REQUEST MADE BY NON-ADMIN')
        remediate(method, info)
        audit_log("REMEDIATED", info, insertId)
        return

    if records_updated('custom_roles.json', method, info) is not True:
        print('REQUEST HAS NO BUILD RECORDS')
        remediate(method, info)
        audit_log("REMEDIATED", info, insertId)
        return

    else:
        print('VALID REQUEST FROM IAM ADMIN - ', principal, method, info)
        audit_log("APPROVED", info, insertId)


def remediate(method, info):
    print("UNDO ACTION: ", method, info)

    iam_api = discovery.build('iam', 'v1', cache_discovery=False)
    
    role = info['role_name']

    # delete and create are same length - function only meant to handle these two methods
    if method[-10:] == "CreateRole":
        print('delete: ', info)
        
        try:
            #remove bindings() # deleting roles through automation is a bad idea.. a role with no bindings is just as effective
            print('REMOVE ALL BINDINGS FOR ', role)
        except Exception as e:
            print(e)


    elif method[-10:] == "DeleteRole":
        print('re-create...: ', info)   
        
        try:
            iam_api.projects().roles().undelete(name=role).execute()
            print('RE-CREATED ', role)
        except Exception as e:
            print(e)

   
        
    else:
        print("METHOD NOT HANDLED: ", method)
    


def records_updated(filename, method, info):
    print("get file for: ", info)   
    data = get_file(filename)
    roles = [ role['name'] for role in data['roles'] ]
    target_role = info['role_name']

    if 'CreateRole' in method and target_role not in roles:
         return False
     
    if 'DeleteRole' in method and target_role in roles:
         return False

    # RETURN BOOLEAN
    return True

def audit_log(action, info, insertId):
    print("[AUDIT] --- ", action, info)
    timestamp = str(datetime.now())
    data = {"action": action, "role_name": info['role_name'], "insertId": insertId, "timestamp": timestamp}

    name = get_file("audit.log")
    with open(name, "a+") as f:
        json.dump(data, f)
        f.write("\n")

    upload_file(name)


###               ###
#  Helper Functions #
###               ###

# write json data to file then upload
def patch_file(name, data):
    name = "/tmp/" + name
    with open(name, 'r') as f:
        json.dump(data, f)

    upload_file(name)

# upload local file to cloud storage
def upload_file(name):
    destination_blob_name = name[5::] # bucket object name - remove '/tmp/'
    blob = bucket.blob(destination_blob_name) # prepare the file for object upload
    try:
        blob.upload_from_filename(name) # upload file as object
    except Exception as e:
         print(e)
         
    print("RECORDS UPDATED:", destination_blob_name)

# get file from cloud storage
def get_file(name):
    destination_file_name = "/tmp/" + name # local file - save to /tmp/ on runtime container
    blob = bucket.blob(name) # prepare the object for file download
    blob.download_to_filename(destination_file_name) # save object as local file
    
    if(name == "audit.log"): # append-only for this file
        return destination_file_name
    
    # get json data from file 
    data = None
    with open(destination_file_name) as f:
        data = json.load(f)

    return(data)


def bad_request(e):
    code = 400
    return(str(e), code)
  
