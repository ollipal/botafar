from gpiozero import LED, Servo
from gpiozero.pins.pigpio import (
    PiGPIOFactory,  # Optional, removes servo stutter!
)

import botafar

"""
An example that combines a servo and four LEDs
with botafar.Joystick and botafar.Button
"""

SERVO_VALUES = {
    "on_left": -1,
    "on_up_left": -0.5,
    "on_up": 0,
    "on_center": 0,
    "on_up_right": 0.5,
    "on_right": 1,
    "on_down_left": None,  # Not in use
    "on_down": None,  # Not in use
    "on_down_right": None,  # Not in use
}

b = botafar.Button("L", alt="SPACE")
j = botafar.Joystick(
    "W", "A", "S", "D", alt=["UP", "LEFT", "DOWN", "RIGHT"], diagonals=True
)

red = LED(27)
yellow = LED(9)
green = LED(10)
blue = LED(22)

servo = Servo(
    17,
    pin_factory=PiGPIOFactory(),
    min_pulse_width=0.544 / 1000,  # Adjust if needed
    max_pulse_width=2.4 / 1000,  # Adjust if needed
)


@b.on_press
def blue_on():
    blue.on()


@b.on_release
def blue_off():
    blue.off()


@j.on_any
def move_servo(event):
    servo_value = SERVO_VALUES[event.name]
    if servo_value is not None:
        botafar.print(f"servo value {servo_value}")
        servo.value = servo_value
        red.off()
        yellow.off()
        green.off()
    elif event.name == "on_down_left":
        red.off()
        yellow.off()
        green.on()
    elif event.name == "on_down":
        red.off()
        yellow.on()
        green.off()
    elif event.name == "on_down_right":
        red.on()
        yellow.off()
        green.off()


botafar.run()
