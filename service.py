from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import yaml
from typing import NamedTuple
import subprocess
import requests
import os


class ConfigTunables(NamedTuple):
    flask_host_address: str
    flask_port: int
    canvas_course_id: str
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
    current_path = os.path.abspath(os.getcwd())
    with open(current_path + '\\\\config.yml', 'r') as file:
        config_file = yaml.safe_load(file)
    return_item = ConfigTunables(config_file['flask']['host_address'],   # 0
                                 config_file['flask']['port'],           # 1
                                 config_file['canvas']['course_id'],     # 2
                                 config_file['canvas']['access_token'],  # 3
                                 config_file['led']['host_address'],     # 4
                                 config_file['led']['port'])             # 5
    return return_item


config = config_parse()
print(config)


def canvas_parse(input_string):
    course_id = config['canvas_course_id']
    token = config['canvas_access_token']
    file = input_string.partition('file=')[2]
    return_item = CanvasInputs(input_string, course_id, token, file)
    return return_item


def led_parse(input_string):
    led_command = input_string.partition('command=')[2]
    tmp = led_command.split('-')
    led_status = tmp[0]
    led_color = tmp[1]
    led_intensity = tmp[2]
    host_address = config['led_host_address']
    port = config['led_port']
    return_item = LEDInputs(input_string, led_command, led_status, led_color, led_intensity, host_address, port)
    return return_item


def canvas_request(input_string):
    c = canvas_parse(input_string)
    r = requests.get('https://vt.instructure.com/api/v1/courses/' + c['course_id'] +
                     '/files/' + c['file'] +
                     '?access_token=' + c['token'])
    return r


def led_request(input_string):
    l = led_parse(input_string)
    r = requests.get('http://' + l['host_address'] + ':' + l['port'] +
                     '/LED?' + l['status'] + '&' + l['color'] + '&' + l['intensity'])
    return r


# class FlaskApplication(Resource):
#     def curl_in(self, curl_input):
#         if curl_input.find('LED?') != -1:
#             led_return = led_request(curl_input)
#         elif curl_input.find('Canvas?') != -1:
#             canvas_return = canvas_request(curl_input)
#         else:
#             print('ERROR')


def main():
    app = Flask(__name__)
    # api = Api(app)
    # api.add_resource(FlaskApplication, '/<string:curl_input>')

    @app.route('/<string:curl_input>')
    def curl_in(self, curl_input):
        if curl_input.find('LED?') != -1:
            led_return = led_request(curl_input)
        elif curl_input.find('Canvas?') != -1:
            canvas_return = canvas_request(curl_input)
        else:
            print('ERROR')
    app.run(host=config[0], port=config[1], debug=True)


def run(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True, shell=True)
    return completed


if __name__ == '__main__':
    # current_path = os.path.abspath(os.getcwd())
    # command0 = run('cd ' + current_path)
    # if command0.returncode != 0:
    #     print("An error occurred:", command0.stderr)
    main()
