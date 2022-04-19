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
    with open(current_path + '\\\\service_config.yml', 'r') as file:
        config_file = yaml.safe_load(file)
    return_item = ConfigTunables(config_file['flask']['host_address'],   # 0
                                 config_file['flask']['port'],           # 1
                                 config_file['canvas']['course_id'],     # 2
                                 config_file['canvas']['access_token'],  # 3
                                 config_file['led']['host_address'],     # 4
                                 config_file['led']['port'])             # 5
    return return_item


config = config_parse()


def canvas_parse(input_string):
    course_id = config[2]
    token = config[3]
    file = input_string
    return_item = CanvasInputs(input_string, course_id, token, file)
    return return_item


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


def canvas_request(input_string):
    c = canvas_parse(input_string)
    r = requests.get('https://vt.instructure.com/api/v1/courses/' + c[1] +
                     '/files/' + c[3] +
                     '?access_token=' + c[2])
    return r


def led_request(input_string):
    l = led_parse(input_string)
    r = requests.get('http://' + l[5] + ':' + str(l[6]) +
                     '/LED?' + l[2] + '&' + l[3] + '&' + l[4])
    return r


def main():
    app = Flask(__name__)

    @app.route('/Canvas')
    def canvas():
        args = request.args
        if 'file' in args:
            filename = args['file']
            print(canvas_request(filename).text)
        return 'DONE\n'

    @app.route('/LED')
    def led():
        args = request.args
        if 'command' in args:
            command = args['command']
            print(led_request(command).text)
        return 'DONE\n'

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
