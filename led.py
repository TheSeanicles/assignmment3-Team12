import time
from zeroconf import Zeroconf, ServiceInfo
import socket
import yaml
from _thread import *
from typing import NamedTuple
# import RPi.GPIO as GPIO

with open('led_config.yml', 'r') as file:
    config_file = yaml.safe_load(file)

# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(32, GPIO.OUT)
# GPIO.setup(36, GPIO.OUT)
# GPIO.setup(38, GPIO.OUT)

ServerSocket = socket.socket()
host = config_file['host_address']
led_port = config_file['port']
socket_size = config_file['socket_size']
ThreadCount = 0

try:
    ServerSocket.bind((host, led_port))
except socket.error as e:
    print(str(e))
ServerSocket.listen(5)


def execute_command(sc, cc, ic):
    red_pin = GPIO.PWM(32, 0.5)
    green_pin = GPIO.PWM(36, 0.5)
    blue_pin = GPIO.PWM(38, 0.5)
    if sc == 'on':
        if cc == 'red':
            red_pin.stop()
            green_pin.stop()
            blue_pin.stop()

            red_pin.start()

        elif cc == 'blue':
            red_pin.stop()
            green_pin.stop()
            blue_pin.stop()

            blue_pin.start()

        elif cc == 'green':
            red_pin.stop()
            green_pin.stop()
            blue_pin.stop()

            green_pin.start()

        elif cc == 'magenta':
            red_pin.stop()
            green_pin.stop()
            blue_pin.stop()

            red_pin.start()
            blue_pin.start()

        elif cc == 'cyan':
            red_pin.stop()
            green_pin.stop()
            blue_pin.stop()

            green_pin.start()
            blue_pin.start()

        elif cc == 'yellow':
            red_pin.stop()
            green_pin.stop()
            blue_pin.stop()

            red_pin.start()
            green_pin.start()

        elif cc == 'white':
            red_pin.stop()
            green_pin.stop()
            blue_pin.stop()

            red_pin.start()
            green_pin.start()
            blue_pin.start()

    elif sc == 'off':
        red_pin.stop()
        green_pin.stop()
        blue_pin.stop()
        GPIO.cleanup()


def threaded_client(connection):
    connection.send(str.encode('CONNECTED'))
    while True:
        data = connection.recv(socket_size)
        if not data:
            break
        print(data)
        command = data.decode('utf-8').partition('LED?')[2].partition(' HTTP')[0]
        status_command = command.partition('&')[0]
        color_command = command.partition('&')[2].partition('&')[0]
        intensity_command = command.partition('&')[2].partition('&')[2]

        commands = {'STATUS': ('on', 'off'),
                    'COLOR': ('red', 'blue', 'green', 'magenta', 'cyan', 'yellow', 'white'),
                    'INTENSITY': '0-255'}

        host_address_bytes = (socket.inet_aton(host),)

        if 0 < led_port < 65535:
            led_service = Zeroconf()
            led_service_info = ServiceInfo(type_='_LED._tcp.local.',
                                           name='rasberrypi._LED._tcp.local.',
                                           addresses=host_address_bytes,
                                           port=led_port,
                                           properties=commands)
            led_service.register_service(info=led_service_info)
            led_service.generate_service_broadcast(info=led_service_info,
                                                   ttl=64,
                                                   broadcast_addresses=True)
            led_service.start()

        if not (status_command in commands['STATUS']):
            print('S')
            connection.sendall(str.encode('Invalid led status.'))
        elif not(color_command in commands['COLOR']):
            print('C')
            connection.sendall(str.encode('Invalid led color.'))
        elif not(0 < int(intensity_command) < 256):
            print(int(intensity_command))
            connection.sendall(str.encode('Invalid led intensity, 0 to 255.'))
        else:
            print('DONE')
            execute_command(status_command, color_command, intensity_command)
            connection.sendall(str.encode('DONE'))
    connection.close()


while True:
    Client, address = ServerSocket.accept()
    print('Accepted client connection from ' + address[0] + ' on port ' + str(address[1]))
    start_new_thread(threaded_client, (Client, ))
    ThreadCount += 1
    # print('Thread Number: ' + str(ThreadCount))
ServerSocket.close()
