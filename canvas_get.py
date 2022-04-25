import requests
import json

token = '4511~WCSGB3WbHDUmamuC5ktWnAWmRvIYbejFoCaG340oJ17IpePXQcka5GsTI6HJX7hW'
course_name = 'Network Application Design'

# GET FILE DOWNLOAD
# /v1/users/{user_id}/files/{id}
parameters = {}
parameters['access_token'] = token
parameters['per_page'] = 1000

c_list = json.loads(requests.get('https://vt.instructure.com/api/v1/courses/', parameters).text)
for c in c_list:
    if 'name' in c:
        if c['name'] == course_name:
            course_id = c['id']

            r0 = requests.get(f'https://vt.instructure.com/api/v1/courses/{course_id}/files/', parameters)

            files = json.loads(r0.text)
            files_dict = {}
            for f in files:
                files_dict[f['display_name']] = f['id']
            print(files_dict)

            selected_file_name = input('Select a file name: ')
            file_id = files_dict[selected_file_name]

            r1 = requests.get(f'https://vt.instructure.com/api/v1/courses/{course_id}/files/{file_id}', parameters)

            file = json.loads(r1.text)
            file_url = json.loads(r1.text)["url"]
            filename = json.loads(r1.text)["display_name"]

            r2 = requests.get(file_url, parameters)
            with open(filename, 'wb') as f:
                f.write(r2.content)



