from flask import Flask, request
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
import time
import yaml
from typing import NamedTuple
import subprocess
import requests
import os


class MyListener(ServiceListener):

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        print(f"Service {name} updated")
        # for ip in info.addresses:
        #     print('IP ADDRESS: ', end='')
        #     print(socket.inet_ntoa(ip))
        # print('PORT: ', end='')
        # print(info.port)
        # status_options = info.properties[b'STATUS'].decode('utf-8')
        # color_options = info.properties[b'COLOR'].decode('utf-8')
        # intensity_options = info.properties[b'INTENSITY'].decode('utf-8')
        # status = info.properties[b'CURRENT_STATUS'].decode('utf-8')
        # color = info.properties[b'CURRENT_COLOR'].decode('utf-8')
        # intensity = info.properties[b'CURRENT_INTENSITY'].decode('utf-8')
        # print('LED STATUS OPTIONS: ', end='')
        # print(status_options)
        # print('LED COLOR OPTIONS: ', end='')
        # print(color_options)
        # print('LED INTENSITY OPTIONS: ', end='')
        # print(intensity_options)
        # print('CURRENT LED STATUS: ', end='')
        # print(status)
        # print('CURRENT LED COLOR: ', end='')
        # print(color)
        # print('CURRENT LED INTENSITY: ', end='')
        # print(intensity)

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} removed")

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        print(f"Service {name} added, service info: ")
        # for ip in info.addresses:
        #     print('IP ADDRESS: ', end='')
        #     print(socket.inet_ntoa(ip))
        # print('PORT: ', end='')
        # print(info.port)
        # status_options = info.properties[b'STATUS'].decode('utf-8')
        # color_options = info.properties[b'COLOR'].decode('utf-8')
        # intensity_options = info.properties[b'INTENSITY'].decode('utf-8')
        # status = info.properties[b'CURRENT_STATUS'].decode('utf-8')
        # color = info.properties[b'CURRENT_COLOR'].decode('utf-8')
        # intensity = info.properties[b'CURRENT_INTENSITY'].decode('utf-8')
        # print('LED STATUS OPTIONS: ', end='')
        # print(status_options)
        # print('LED COLOR OPTIONS: ', end='')
        # print(color_options)
        # print('LED INTENSITY OPTIONS: ', end='')
        # print(intensity_options)
        # print('CURRENT LED STATUS: ', end='')
        # print(status)
        # print('CURRENT LED COLOR: ', end='')
        # print(color)
        # print('CURRENT LED INTENSITY: ', end='')
        # print(intensity)


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
    r = requests.get(url='https://vt.instructure.com/api/v1/courses/' + c[1] +
                     '/files/' + c[3] +
                     '?access_token=' + c[2])
    return r


def led_request(input_string, status, color, intensity):
    l = led_parse(input_string)
    if not(l[2] in status):
        print(f"{l[2]} not a choice of {status}")
        return
    elif not(l[3] in color):
        print(f"{l[3]} not in colors {color}")
        return
    elif not(l[4] in intensity):
        print(f"{l[4]} not in intensity range 0 to 255")
        return
    r = requests.get(url='http://' + l[5] + ':' + str(l[6]) +
                    '/LED?status=' + l[2] + '&color=' + l[3] + '&intensity=' + l[4],
                     headers={'Connection': 'close'})
    return r


def main():
    zeroconf = Zeroconf()
    listener = MyListener()
    ServiceBrowser(zeroconf, "_LED._tcp.local.", listener)
    info = zeroconf.get_service_info('_LED._tcp.local.', 'rasberrypi._LED._tcp.local.')
    while info == None:
        print('No pi LED found retrying in: ',end='')
        print('5',end='')
        time.sleep(0.25)
        print('.', end='')
        time.sleep(0.25)
        print('.', end='')
        time.sleep(0.25)
        print('.', end='')
        time.sleep(0.25)
        print('4', end='')
        time.sleep(0.25)
        print('.', end='')
        time.sleep(0.25)
        print('.', end='')
        time.sleep(0.25)
        print('.', end='')
        time.sleep(0.25)
        print('3', end='')
        time.sleep(0.25)
        print('.', end='')
        time.sleep(0.25)
        print('.', end='')
        time.sleep(0.25)
        print('.', end='')
        time.sleep(0.25)
        print('2', end='')
        time.sleep(0.25)
        print('.', end='')
        time.sleep(0.25)
        print('.', end='')
        time.sleep(0.25)
        print('.', end='')
        time.sleep(0.25)
        print('1', end='')
        time.sleep(0.25)
        print('.', end='')
        time.sleep(0.25)
        print('.', end='')
        time.sleep(0.25)
        print('.')
        info = zeroconf.get_service_info('_LED._tcp.local.', 'rasberrypi._LED._tcp.local.')
    status_options = info.properties[b'STATUS'].decode('utf-8')
    color_options = info.properties[b'COLOR'].decode('utf-8')
    intensity_options = info.properties[b'INTENSITY'].decode('utf-8')

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
            print(led_request(command, status_options, color_options, intensity_options).text)
        return 'DONE\n'

    app.run(host=config[0], port=config[1], debug=True)


def run(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True, shell=True)
    return completed


if __name__ == '__main__':
    main()
