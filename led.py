import time
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
from typing import NamedTuple
import RPi.GPIO as GPIO

class MyListener(ServiceListener):

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} updated")

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} removed")

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        print(f"Service {name} added, service info: {info}")


zeroconf = Zeroconf()
listener = MyListener()
browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
try:
    input("Press enter to exit...\n\n")
finally:
    zeroconf.close()
























# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(32, GPIO.OUT)
# GPIO.setup(36, GPIO.OUT)
# GPIO.setup(38, GPIO.OUT)
#
# red_pin = GPIO.PWM(32, 0.5)
# green_pin = GPIO.PWM(36, 0.5)
# blue_pin = GPIO.PWM(38, 0.5)
#
# red_pin.start()
# green_pin.start()
# blue_pin.start()
#
# red_pin.stop()
# green_pin.stop()
# blue_pin.stop()
#
# GPIO.cleanup()
#
#
# class LED(NamedTuple):
#     status: str
#     color: str
#     intensity: int
#
#
# def on_off_select(input_string):
#     if input_string == 'on':
#         return 1
#     elif input_string == 'off':
#         return 0
#     else:
#         return -1
#
#
# def color_select(input_string):
#     if input_string == 'red':
#         pass
#     elif input_string == 'blue':
#         pass
#     elif input_string == 'green':
#         pass
#     elif input_string == 'magenta':
#         pass
#     elif input_string == 'cyan':
#         pass
#     elif input_string == 'yellow':
#         pass
#     elif input_string == 'white':
#         pass
#     else:
#         print('UNSUPPORTED COLOR')
#
#
# def execute_command():
#     pass