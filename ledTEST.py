import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)
GPIO.setup(36, GPIO.OUT)
GPIO.setup(38, GPIO.OUT)


def execute_command(sc, cc, ic):
    duty_cycle = int(ic) / 255
    red_pin = GPIO.PWM(32, 500)
    green_pin = GPIO.PWM(36, 500)
    blue_pin = GPIO.PWM(38, 500)
    if sc == 'on':
        if cc == 'red':
            red_pin.start(duty_cycle)
            time.sleep(2)

        elif cc == 'blue':
            blue_pin.start(duty_cycle)
            time.sleep(2)

        elif cc == 'green':
            green_pin.start(duty_cycle)
            time.sleep(2)

        elif cc == 'magenta':
            red_pin.start(duty_cycle)
            blue_pin.start(duty_cycle)
            time.sleep(2)

        elif cc == 'cyan':
            green_pin.start(duty_cycle)
            blue_pin.start(duty_cycle)
            time.sleep(2)

        elif cc == 'yellow':
            red_pin.start(duty_cycle)
            green_pin.start(duty_cycle)
            time.sleep(2)

        elif cc == 'white':
            red_pin.start(duty_cycle)
            green_pin.start(duty_cycle)
            blue_pin.start(duty_cycle)
            time.sleep(2)

    elif sc == 'off':
        red_pin.stop()
        green_pin.stop()
        blue_pin.stop()
        GPIO.cleanup()


execute_command('on', 'red', '255')
execute_command('on', 'blue', '255')
execute_command('on', 'green', '255')
execute_command('on', 'magenta', '255')
execute_command('on', 'cyan', '255')
execute_command('on', 'yellow', '255')
execute_command('on', 'white', '255')
GPIO.cleanup()