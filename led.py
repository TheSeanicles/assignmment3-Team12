from zeroconf import Zeroconf, ServiceInfo
import socket
import yaml
import time
import multiprocessing
from _thread import *
import RPi.GPIO as GPIO


with open('led_config.yml', 'r') as file:
    config_file = yaml.safe_load(file)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)
GPIO.setup(36, GPIO.OUT)
GPIO.setup(38, GPIO.OUT)

red_pin = GPIO.PWM(32, 500)
green_pin = GPIO.PWM(36, 500)
blue_pin = GPIO.PWM(38, 500)

ServerSocket = socket.socket()
host = config_file['host_address']
led_port = config_file['port']
socket_size = config_file['socket_size']
ThreadCount = 0

led_zeroconf_stats = {'STATUS': ('on', 'off'),
                      'COLOR': ('red', 'blue', 'green', 'magenta', 'cyan', 'yellow', 'white'),
                      'INTENSITY': '0-255',
                      'CURRENT_STATUS': 'off',
                      'CURRENT_COLOR': 'white',
                      'CURRENT_INTENSITY': '0'}


host_address_bytes = [socket.inet_aton(host)]

if 0 < led_port < 65535:
    led_service = Zeroconf()
    led_service_info = ServiceInfo(type_='_LED._tcp.local.',
                                   name='rasberrypi._LED._tcp.local.',
                                   addresses=host_address_bytes,
                                   properties=led_zeroconf_stats,
                                   port=led_port)
    # led_service.register_service(info=led_service_info)
    # led_service.generate_service_broadcast(info=led_service_info,
    #                                        ttl=64,
    #                                        broadcast_addresses=True)
    led_service.start()


try:
    ServerSocket.bind((host, led_port))
except socket.error as e:
    print(str(e))
ServerSocket.listen(5)


def execute_command(sc, cc, ic):
    led_zeroconf_stats['CURRENT_STATUS'] = sc
    led_zeroconf_stats['CURRENT_COLOR'] = cc
    led_zeroconf_stats['CURRENT_INTENSITY'] = ic
    updated_info = ServiceInfo(type_='_LED._tcp.local.',
                               name='rasberrypi._LED._tcp.local.',
                               addresses=host_address_bytes,
                               properties=led_zeroconf_stats,
                               port=led_port)
    led_service.update_service(updated_info)
    duty_cycle = int(ic) / 255
    if sc == 'on':
        if cc == 'red':
            red_pin.start(duty_cycle)

        elif cc == 'blue':
            blue_pin.start(duty_cycle)

        elif cc == 'green':
            green_pin.start(duty_cycle)

        elif cc == 'magenta':
            red_pin.start(duty_cycle)
            blue_pin.start(duty_cycle)

        elif cc == 'cyan':
            green_pin.start(duty_cycle)
            blue_pin.start(duty_cycle)

        elif cc == 'yellow':
            red_pin.start(duty_cycle)
            green_pin.start(duty_cycle)

        elif cc == 'white':
            red_pin.start(duty_cycle)
            green_pin.start(duty_cycle)
            blue_pin.start(duty_cycle)

    elif sc == 'off':
        red_pin.stop()
        green_pin.stop()
        blue_pin.stop()


def threaded_client(connection):
    data = connection.recv(socket_size)
    if data:
        print(data)
        command = data.decode('utf-8').partition('LED?')[2].partition(' HTTP')[0]
        status_command = command.partition('status=')[2].partition('&')[0]
        color_command = command.partition('color=')[2].partition('&')[0]
        intensity_command = command.partition('intensity=')[2]

        if not (status_command in led_zeroconf_stats['STATUS']):
            print('Invalid led status.')
            connection.send(str.encode('HTTP/1.1 200 OK\r\nConnection: close'))
        elif not(color_command in led_zeroconf_stats['COLOR']):
            print('Invalid led color.')
            connection.send(str.encode('HTTP/1.1 200 OK\r\nConnection: close'))
        elif not(0 <= int(intensity_command) <= 255):
            print('Invalid led intensity, 0 to 255.')
            connection.send(str.encode('HTTP/1.1 200 OK\r\nConnection: close'))
        else:
            execute_command(status_command, color_command, intensity_command)
            print('DONE')
            connection.send(str.encode('HTTP/1.1 200 OK\r\nConnection: close'))
    connection.close()


execute_command('off', 'white', '0',)
while True:
    Client, address = ServerSocket.accept()
    print('Accepted client connection from ' + address[0] + ' on port ' + str(address[1]))
    start_new_thread(threaded_client, (Client,))
    ThreadCount += 1
    # print('Thread Number: ' + str(ThreadCount))
ServerSocket.close()
GPIO.cleanup()


