import os
import json
from google.cloud import storage
from datetime import datetime

storage_client = storage.Client()
bucket_name = 'your_bucket_name'
bucket = storage_client.bucket(bucket_name)
project_id = os.environ.get('GCP_PROJECT')

def role_record_keeper(request):
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
        action = None ; role = None ; perms = None
        try:
            action = msg['action'] ; role = msg['role_name'] ; perms = msg['permissions']
            print(action, role, perms)
        except Exception as e:
            print(e)
            return(bad_request(e))
        
        if action == 'CREATE':  
            print("create role..")
            create_role(role, perms)         
        elif action == 'DELETE':
            print("delete role.. and all bindings..")
            delete_role(role)
            # call bindings_record_keepr
        elif action == 'UPDATE':
            print('update role permissions.. ')
            update_role(role, perms)
        else:
            bad_request("BAD REQUEST -- UNRECOGNIZED ACTION")

        # return status 200
        audit_log(msg)
        return('SUCCESS')
    
    else:
        return(bad_request('BAD REQUEST'))


def create_role(role, perms):
    print('adding role...', role)
    data = get_file("custom_roles.json")
    role_title = role[role.find('roles/')+6::] # get role_id
    entry = {"name": role, "title": role_title, "includedPermissions": perms}
    data['roles'].append(entry)
    print("UPDATED: ", data)
    
    # write json to file and upload
    patch_file('custom_roles.json', data)


def delete_role(role):
    print('removing role...', role)
    data = get_file("custom_roles.json")
    print(data)
    
    # find entry and delete
    for r in data['roles']:
        if r['name'] == role:
            data['roles'].remove(r)
            print("UPDATED: ", data)

            # write json to file and upload
            patch_file('custom_roles.json', data)

def update_role(role, perms):
    print('updating role...', role)
    data = get_file("custom_roles.json")
    role_title = role[role.find('roles/')+6::] # get role_id
    entry = {"name": role, "title": role_title, "includedPermissions": perms}
    
    print('roles: ', data)
    for target_role in data['roles']:
        if target_role['name'] == role:
            print('BEFORE: ', target_role['includedPermissions'])
            target_role['includedPermissions'] = perms
            print("AFTER: ", target_role['includedPermissions'])
    
    #data['roles'].append(entry)
    print("UPDATED: ", data)
    
    # write json to file and upload
    patch_file('custom_roles.json', data)

# make this a pubsub call to bindings func...
def remove_binding(members, role):
    pass

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
    res_type = "iam_role"
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

