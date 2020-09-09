import os
import json
from google.cloud import storage
from datetime import datetime

storage_client = storage.Client()
bucket_name = 'your_bucket_name'
bucket = storage_client.bucket(bucket_name)
project_id = os.environ.get('GCP_PROJECT')

def service_account_records(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    if 'message' in request_json:
        msg = request_json['message']
        print(msg)
        
        # make sure there's an 'action'
        action = None ; sa = None
        try:
            action = msg['action'] ; sa = msg['account_id']
            print(action, sa)
        except Exception as e:
            print(e)
            return(bad_request(e))

        # create/modify/delete artifact    
        if action == 'CREATE':  
            print("create sa..")
            create_sa(sa)         
        elif action == 'DELETE':
            print("delete sa.. and all bindings..")
            delete_sa(sa)
            #remove_binding(sa)
        else:
            bad_request("BAD REQUEST -- UNRECOGNIZED ACTION")

        # return status 200
        audit_log(msg)
        return('SUCCESS')
    
    else:
        return(bad_request('BAD REQUEST'))


def create_sa(sa):
    print('adding service account...', sa)
    data = get_file("service_accounts.json")
    
    # json entry
    email = sa + "@" + project_id + ".iam.gserviceaccount.com"
    name = "projects/" + project_id + "/serviceAccounts/" + email
    displayName = sa
    entry = {"name": name, "email": email, "displayName": displayName}
    # modify in-place   
    data['accounts'].append(entry)
    print("UPDATED: ", data)
    
    # write json to file and upload
    patch_file('service_accounts.json', data)


def delete_sa(sa):
    print('removing service account...', sa)
    data = get_file("service_accounts.json")
    print(data)
    
    # find entry and delete
    for account in data['accounts']:
        if account['displayName'] == sa:
            data['accounts'].remove(account)
            print("UPDATED: ", data)

            # write json to file and upload
            patch_file('service_accounts.json', data)


def remove_binding(members, role):
    print('removing binding...', members, role)
    data = get_file("bindings.json")
    print(data)

    # find entry and delete
    for binding in data['bindings']:
        for existing_member in binding['members']:
            for target_member in members:
                if target_member == existing_member:
                    data['bindings'].remove(binding)
                    print("UPDATED: ", data)

                    # write json to file and upload
                    patch_file('bindings.json', data)



###               ###
#  Helper Functions #
###               ###

# write json data to file then upload
def patch_file(name, data):
    name = "/tmp/" + name
    with open(name, 'w') as f:
        json.dump(data, f)


    upload_file(name)

def audit_log(msg):
    res_type = "service_account"
    timestamp = str(datetime.now())
    msg.update({"type": res_type, "timestamp": timestamp})
    print("[AUDIT] --- ", msg)

    name = get_file("audit.log")
    with open(name, 'a+') as f:
        json.dump(msg, f)
        f.write("\n")

    upload_file(name)

# upload local file to cloud storage
def upload_file(name):
    source_file_name = name  # local file 
    destination_blob_name = name[5::] # bucket object name - remove '/tmp/'
    blob = bucket.blob(destination_blob_name) # prepare the file for object upload
    blob.upload_from_filename(source_file_name) # upload file as object

    print("RECORDS UPDATED:", destination_blob_name)

# get file from cloud storage
def get_file(name):
    source_blob_name = name # bucket object
    destination_file_name = "/tmp/" + name # local file - save to /tmp/ on runtime container
    blob = bucket.blob(source_blob_name) # prepare the object for file download
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

