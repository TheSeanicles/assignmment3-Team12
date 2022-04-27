from flask import Flask, request
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
from flask_httpauth import HTTPBasicAuth
from pymongo import MongoClient
import time
import yaml
import socket
from typing import NamedTuple
import subprocess
import requests
import json
from collections import OrderedDict


class MyListener(ServiceListener):

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        print(f"Service {name} updated")
        # for ip in info.addresses:
        #     print(f'IP ADDRESS: {socket.inet_ntoa(ip)}')
        # print(f'PORT: {info.port}')
        # status_options = info.properties[b'STATUS'].decode('utf-8')
        # color_options = info.properties[b'COLOR'].decode('utf-8')
        # intensity_options = info.properties[b'INTENSITY'].decode('utf-8')
        # status = info.properties[b'CURRENT_STATUS'].decode('utf-8')
        # color = info.properties[b'CURRENT_COLOR'].decode('utf-8')
        # intensity = info.properties[b'CURRENT_INTENSITY'].decode('utf-8')
        # print(f'LED STATUS OPTIONS: {status_options}')
        # print(f'LED COLOR OPTIONS: {color_options}')
        # print(f'LED INTENSITY OPTIONS: {intensity_options}')
        # print(f'CURRENT LED STATUS: {status}')
        # print(f'CURRENT LED COLOR: {color}')
        # print(f'CURRENT LED INTENSITY: {intensity}')

        # time.sleep(10)

        with open('service_config.yml', 'r') as file:
            dict_file = yaml.safe_load(file)

        try:
            dict_file['led']['host_address'] = str(socket.inet_ntoa(info.addresses[0]))
            dict_file['led']['port'] = info.port

            with open(r'service_config.yml', 'w') as file:
                yaml.dump(dict_file, file)

        except TypeError:
            with open(r'service_config.yml', 'w') as file:
                yaml.dump(dict_file, file)

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} removed")

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        print(f"Service {name} added")
        # for ip in info.addresses:
        #     print(f'IP ADDRESS: {socket.inet_ntoa(ip)}')
        # print(f'PORT: {info.port}')
        # status_options = info.properties[b'STATUS'].decode('utf-8')
        # color_options = info.properties[b'COLOR'].decode('utf-8')
        # intensity_options = info.properties[b'INTENSITY'].decode('utf-8')
        # status = info.properties[b'CURRENT_STATUS'].decode('utf-8')
        # color = info.properties[b'CURRENT_COLOR'].decode('utf-8')
        # intensity = info.properties[b'CURRENT_INTENSITY'].decode('utf-8')
        # print(f'LED STATUS OPTIONS: {status_options}')
        # print(f'LED COLOR OPTIONS: {color_options}')
        # print(f'LED INTENSITY OPTIONS: {intensity_options}')
        # print(f'CURRENT LED STATUS: {status}')
        # print(f'CURRENT LED COLOR: {color}')
        # print(f'CURRENT LED INTENSITY: {intensity}'))

        # time.sleep(10)

        with open('service_config.yml', 'r') as file:
            dict_file = yaml.safe_load(file)

        try:
            dict_file['led']['host_address'] = str(socket.inet_ntoa(info.addresses[0]))
            dict_file['led']['port'] = info.port

            with open(r'service_config.yml', 'w') as file:
                yaml.dump(dict_file, file)

        except TypeError:
            with open(r'service_config.yml', 'w') as file:
                yaml.dump(dict_file, file)


class ConfigTunables(NamedTuple):
    flask_host_address: str
    flask_port: int
    canvas_course_name: str
    canvas_access_token: str
    led_host_address: str
    led_port: int


class HTTPAuth(NamedTuple):
    user: str
    pwd: str


class CanvasInputs(NamedTuple):
    http_raw: str
    course_id: str
    token: str
    file: str


class LEDInputs(NamedTuple):
    http_raw: str
    led_command: str
    status: str
    color: str
    intensity: str
    host_address: str
    port: int


def config_parse():
    # Use Yaml library to parse config program tunables
    with open('service_config.yml', 'r') as file:
        config_file = yaml.safe_load(file)
    return_item = ConfigTunables(config_file['flask']['host_address'],   # 0
                                 config_file['flask']['port'],           # 1
                                 config_file['canvas']['course_name'],   # 2
                                 config_file['canvas']['access_token'],  # 3
                                 config_file['led']['host_address'],     # 4
                                 config_file['led']['port'])             # 5
    return return_item


config = config_parse()


def led_parse(input_string):
    led_command = input_string
    tmp = led_command.split('-')
    led_status = tmp[0]
    led_color = tmp[1]
    led_intensity = tmp[2]
    host_address = config[4]
    port = config[5]
    return_item = LEDInputs(input_string, led_command, led_status, led_color, led_intensity, host_address, port)
    return return_item


def canvas_get_request(filename):
    course_name = config[2]

    # GET FILE DOWNLOAD
    # /v1/users/{user_id}/files/{id}
    parameters = {}
    parameters['access_token'] = config[3]
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
                # print(files_dict)

                if filename in files_dict:
                    file_id = files_dict[filename]

                    r1 = requests.get(f'https://vt.instructure.com/api/v1/courses/{course_id}/files/{file_id}', parameters)

                    file_url = json.loads(r1.text)["url"]

                    r2 = requests.get(file_url, parameters)
                    with open(filename, 'wb') as f:
                        f.write(r2.content)
                    return r2.text
                else:
                    return 'File not found'


def canvas_post_request(filename):
    # GET MY FILE location
    parameters = OrderedDict()
    parameters['access_token'] = config[3]
    parameters['per_page'] = 1000

    base_url = 'https://vt.instructure.com/api/v1'

    # Find users id

    api_call = '/users/self/profile/'

    r0 = requests.get(base_url + api_call, parameters)

    user_id = json.loads(r0.text)['id']

    # find Users my files folder

    api_call = f'/users/{user_id}/folders/'

    r1 = requests.get(base_url + api_call, parameters)

    folders = json.loads(r1.text)

    for f in folders:
        if f['name'] == 'my files':
            folder_id = f['id']

    # POST FILE UPLOAD
    # /v1/folders/{folder_id}/files
    # https://canvas.instructure.com/doc/api/file.file_uploads.html

    api_call = f'/folders/{folder_id}/files'

    parameters['filename'] = filename

    r2 = requests.post(base_url + api_call, parameters)

    upload_url = json.loads(r2.text)['upload_url']

    upload_params = json.loads(r2.text)['upload_params']

    # print(r2.text)

    del parameters['access_token']
    del parameters['per_page']
    del parameters['filename']

    parameters['filename'] = upload_params['filename']

    parameters['content_type'] = upload_params['content_type']

    try:
        file = open(filename, 'rb')

        parameters['file'] = file

        files = {'file': file}

        r3 = requests.post(upload_url, files=files)

        return r3.text

    except:
        return 'File not found'


def led_post_request(input_string, status, color, intensity):
    set_l = led_parse(input_string)
    if not(set_l[2] in status):
        print(f"{set_l[2]} not a choice of {status}")
        return
    elif not(set_l[3] in color):
        print(f"{set_l[3]} not in colors {color}")
        return
    elif not(0 <= int(set_l[4]) <= 255):
        print(f"{set_l[4]} not in intensity range 0 to 255")
        return
    r = requests.post(url='http://' + set_l[5] + ':' + str(set_l[6]) +
                      '/LED?status=' + set_l[2] + '&color=' + set_l[3] + '&intensity=' + set_l[4],
                      headers={'Connection': 'close'})
    return r


def led_get_request():
    r = requests.get(url='http://' + config[4] + ':' + str(config[5]) + '/LED',
                     headers={'Connection': 'close'})
    return r


def main():
    zeroconf = Zeroconf()
    listener = MyListener()
    ServiceBrowser(zeroconf, "_LED._tcp.local.", listener)
    info = zeroconf.get_service_info('_LED._tcp.local.', 'raspberrypi._LED._tcp.local.')

    while info is None:
        print('No pi LED found retrying in 5 seconds.')
        time.sleep(5)
        info = zeroconf.get_service_info('_LED._tcp.local.', 'raspberrypi._LED._tcp.local.')

    # time.sleep(5)

    status_options = info.properties[b'STATUS'].decode('utf-8')

    color_options = info.properties[b'COLOR'].decode('utf-8')

    intensity_options = info.properties[b'INTENSITY'].decode('utf-8')

    app = Flask(__name__)
    auth = HTTPBasicAuth()

    # https://127.0.0.1:5000/Canvas?file=<filename>&operation=<upload or download>

    @app.route('/Canvas', methods=['GET', 'POST'])
    @auth.login_required(optional=True)
    def canvas():
        user = auth.current_user()
        if user is not False:  # if the user is valid, aka it exists
            args = request.args
            if 'operation' in args:
                if 'file' in args:
                    filename = args['file']
                    operation = args['operation']
                    if operation == 'upload':
                        r = canvas_post_request(filename)
                        if r == 'File not found':
                            return 'File not found\n'
                        else:
                            return 'DONE\n'
                    elif operation == 'download':
                        canvas_get_request(filename)
                        return 'DONE\n'
                else:
                    return 'No file parameter\n'
            else:
                # No operation detected
                if 'file' in args:
                    filename = args['file']
                    if request.method == 'GET':
                        r = canvas_get_request(filename)
                        if r == 'File not found':
                            return 'File not found\n'
                        else:
                            return 'DONE\n'
                    elif request.method == 'POST':
                        print(request.files)
                        f = request.files['file']
                        f.save(filename)
                        r = canvas_post_request(filename)
                        if r == 'File not found':
                            return 'File not found\n'
                        else:
                            return 'DONE\n'
                    else:
                        return 'Method was neither POST or GET\n'
                else:
                    return 'No file parameter\n'
        else:
            return 'Could not verify your access level for that URL.  You have to login with proper credentials\n'

    # https://127.0.0.1:5000/LED?command=<status>-<color>-<intensity>

    @app.route('/LED', methods=['GET', 'POST'])
    @auth.login_required(optional=True)
    def led():
        user = auth.current_user()
        if user is not False:  # if the user is valid, aka it exists
            args = request.args
            if 'command' in args and request.method == 'POST':
                command = args['command']
                led_post_request(command, status_options, color_options, intensity_options)
                return 'DONE\n'
            elif request.method == 'GET':
                return led_get_request().text
            else:
                return 'Method was neither POST or GET\n'
        else:
            return 'Could not verify your access level for that URL.  You have to login with proper credentials\n'

    @auth.verify_password
    def verify_password(username, password):
        mongoclient = MongoClient("mongodb://localhost:27017")
        db = mongoclient["ECE4564_Assignment_3"]
        col = db["service_auth"]
        x = col.find_one({"username": username, "password": password})
        if x is None:
            return False
        return x["username"]

    app.run(host=config[0], port=config[1], debug=True)


if __name__ == '__main__':
    main()
