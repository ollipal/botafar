from gpiozero import LED, Servo
from gpiozero.pins.pigpio import (
    PiGPIOFactory,  # Optional, removes servo stutter!
)

import botafar

"""
An example that combines a servo and four LEDs
with botafar.Joystick and botafar.Button
"""

b = botafar.Button("L", alt="SPACE")
j = botafar.Joystick("W", "A", "S", "D", alt=["UP", "LEFT", "DOWN", "RIGHT"])

red = LED(27)
yellow = LED(9)
green = LED(10)
blue = LED(22)


def turn_green_yellow_red_off():
    red.off()
    yellow.off()
    green.off()


servo = Servo(
    17,
    pin_factory=PiGPIOFactory(),
    min_pulse_width=0.544 / 1000,  # Adjust if needed
    max_pulse_width=2.4 / 1000,  # Adjust if needed
)


@b.on_press
def blue_on():
    botafar.print("blue on")
    blue.on()


@b.on_release
def blue_off():
    botafar.print("blue off")
    blue.off()


@j.on_left
def servo_left():
    botafar.print("servo value 1")
    servo.value = 1
    turn_green_yellow_red_off()


@j.on_up_left
def servo_up_left():
    botafar.print("servo value 0.5")
    servo.value = 0.5
    turn_green_yellow_red_off()


@j.on_up
@j.on_center
def servo_middle():
    botafar.print("servo value 0")
    servo.value = 0
    turn_green_yellow_red_off()


@j.on_up_right
def servo_up_right():
    botafar.print("servo value -0.5")
    servo.value = -0.5
    turn_green_yellow_red_off()


@j.on_right
def servo_right():
    botafar.print("servo value -1")
    servo.value = -1
    turn_green_yellow_red_off()


@j.on_down_left
def green_on():
    botafar.print("green on")
    servo.value = 0
    red.off()
    yellow.off()
    green.on()


@j.on_down
def yellow_on():
    botafar.print("yellow on")
    servo.value = 0
    red.off()
    yellow.on()
    green.off()


@j.on_down_right
def red_on():
    botafar.print("red on")
    servo.value = 0
    red.on()
    yellow.off()
    green.off()


botafar.run()
