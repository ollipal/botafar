from gpiozero import Servo
from gpiozero.pins.pigpio import (
    PiGPIOFactory,  # Optional, removes servo stutter!
)

import botafar

"""
Servo example with a custom class, immediate movement to the target value.
"""

SERVO_GPIO_PIN = 17
SERVO_VALUES = {
    "on_left": 1,
    "on_up_left": 0.5,
    "on_up": 0,
    "on_center": 0,
    "on_up_right": -0.5,
    "on_right": -1,
}


j = botafar.Joystick(
    "W", "A", "S", "D", alt=["UP", "LEFT", "DOWN", "RIGHT"], diagonals=True
)


class ImmediateServo:
    def __init__(self):
        self.servo = Servo(
            SERVO_GPIO_PIN,
            pin_factory=PiGPIOFactory(),
            min_pulse_width=0.544 / 1000,  # Adjust if needed
            max_pulse_width=2.4 / 1000,  # Adjust if needed
        )

    @j.on_any
    def move_servo(self, event):
        servo_value = SERVO_VALUES.get(event.name)
        if servo_value is not None:
            botafar.print(f"servo value {servo_value}")
            self.servo.value = servo_value


ImmediateServo()
botafar.run()
