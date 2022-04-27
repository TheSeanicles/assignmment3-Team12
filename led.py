from zeroconf import Zeroconf, ServiceInfo
import yaml
import socket
import RPi.GPIO as GPIO
from flask import Flask, request


with open('led_config.yml', 'r') as file:
    config_file = yaml.safe_load(file)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)
GPIO.setup(36, GPIO.OUT)
GPIO.setup(38, GPIO.OUT)

red_pin = GPIO.PWM(32, 500)
green_pin = GPIO.PWM(36, 500)
blue_pin = GPIO.PWM(38, 500)

led_port = config_file['port']

led_zeroconf_stats = {'STATUS': ('on', 'off'),
                      'COLOR': ('red', 'blue', 'green', 'magenta', 'cyan', 'yellow', 'white'),
                      'INTENSITY': '0-255',
                      'CURRENT_STATUS': 'off',
                      'CURRENT_COLOR': 'white',
                      'CURRENT_INTENSITY': '0'}

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
host = s.getsockname()[0]
# host = '127.0.0.1'
host_address_bytes = [socket.inet_aton(host)]

if 0 < led_port < 65535:
    led_service = Zeroconf()
    led_service_info = ServiceInfo(type_='_LED._tcp.local.',
                                   name='raspberrypi._LED._tcp.local.',
                                   addresses=host_address_bytes,
                                   properties=led_zeroconf_stats,
                                   port=led_port)
    led_service.register_service(info=led_service_info)
    # led_service.generate_service_broadcast(info=led_service_info,
    #                                        ttl=64,
    #                                        broadcast_addresses=True)
    led_service.start()


def execute_command(sc, cc, ic):
    led_zeroconf_stats['CURRENT_STATUS'] = sc
    led_zeroconf_stats['CURRENT_COLOR'] = cc
    led_zeroconf_stats['CURRENT_INTENSITY'] = ic
    updated_info = ServiceInfo(type_='_LED._tcp.local.',
                               name='raspberrypi._LED._tcp.local.',
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


def main():
    try:
        app = Flask(__name__)

        @app.route('/LED', methods=['POST'])
        def led_post():
            args = request.args
            execute_command('off', 'white', '0')
            if 'status' in args:
                if args['status'] in led_zeroconf_stats['STATUS']:
                    status_command = args['status']
                else:
                    print('Invalid status.')
            else:
                status_command = led_zeroconf_stats['CURRENT_STATUS']
            if 'color' in args:
                if args['color'] in led_zeroconf_stats['COLOR']:
                    color_command = args['color']
                else:
                    print('Invalid color.')
            else:
                color_command = led_zeroconf_stats['CURRENT_COLOR']
            if 'intensity' in args:
                try:
                    if 0 <= int(args['intensity']) <= 255:
                        intensity_command = args['intensity']
                    else:
                        print('Invalid intensity.')
                except TypeError:
                    print('Intensity must be an int between 0 and 255')
            else:
                intensity_command = led_zeroconf_stats['CURRENT_INTENSITY']
            execute_command(status_command, color_command, intensity_command)
            return 'DONE\n'

        @app.route('/LED', methods=['GET'])
        def led_get():
            return f"Current Status: {led_zeroconf_stats['CURRENT_STATUS']}, Current Color: {led_zeroconf_stats['CURRENT_COLOR']}, Current Intensity, {led_zeroconf_stats['CURRENT_INTENSITY']}\n"

        app.run(host=host, port=led_port, debug=True)

    except:
        print('There was an error')
        GPIO.cleanup()


if __name__ == '__main__':
    main()