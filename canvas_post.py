import requests
import json
from collections import OrderedDict

token = '4511~WCSGB3WbHDUmamuC5ktWnAWmRvIYbejFoCaG340oJ17IpePXQcka5GsTI6HJX7hW'
filename = 'Assignment 1 Rubric_rev2.pdf'

# GET MY FILE location
parameters = OrderedDict()
parameters['access_token'] = token
parameters['per_page'] = 1000

base_url = 'https://vt.instructure.com/api/v1'

# Find users id

api_call = '/users/self/profile/'

r0 = requests.get(base_url+api_call, parameters)

user_id = json.loads(r0.text)['id']


# find Users my files folder

api_call = f'/users/{user_id}/folders/'

r1 = requests.get(base_url+api_call, parameters)

folders = json.loads(r1.text)

for f in folders:
    if f['name'] == 'my files':
        folder_id = f['id']


# POST FILE UPLOAD
# /v1/folders/{folder_id}/files
# https://canvas.instructure.com/doc/api/file.file_uploads.html

api_call = f'/folders/{folder_id}/files'

parameters['filename'] = filename

r2 = requests.post(base_url+api_call, parameters)

upload_url = json.loads(r2.text)['upload_url']

upload_params = json.loads(r2.text)['upload_params']

print(r2.text)

del parameters['access_token']
del parameters['per_page']
del parameters['filename']

parameters['filename'] = upload_params['filename']

parameters['content_type'] = upload_params['content_type']

file = open(filename, 'rb')

parameters['file'] = file

files = {'file': file}


r3 = requests.post(upload_url, files=files)

print(r3.text)
