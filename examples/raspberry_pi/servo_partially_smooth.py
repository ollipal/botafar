from threading import Lock
from time import sleep

from gpiozero import Servo
from gpiozero.pins.pigpio import (
    PiGPIOFactory,  # Optional, removes servo stutter!
)

import botafar

"""
Servo example with a custom class, smooth movement to the target value,
immediate return to center.

Adjust SERVO_STEPS and SERVO_UPDATE_FREQ to alter movement speed and
smoothness.
"""

SERVO_GPIO_PIN = 17
SERVO_STEPS = 40
SERVO_UPDATE_FREQ = 25
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


class PartiallySmoothServo:
    def __init__(self):
        self.servo = Servo(
            SERVO_GPIO_PIN,
            pin_factory=PiGPIOFactory(),
            min_pulse_width=0.544 / 1000,  # Adjust if needed
            max_pulse_width=2.4 / 1000,  # Adjust if needed
        )
        self.target_value = 0
        self.sleep_amount = 1 / SERVO_UPDATE_FREQ
        self.move_amount = 2 / SERVO_STEPS
        self.lock = Lock()  # Fixes concurrency issues

    @j.on_any
    def move_servo(self, event):
        with self.lock:
            target_value = SERVO_VALUES.get(event.name)
            if target_value is not None:
                botafar.print(f"servo target value {target_value}")
                while event.is_active and target_value != self.servo.value:

                    if target_value == 0:
                        self.servo.value = target_value
                    elif target_value < self.servo.value:
                        self.servo.value = max(
                            target_value, self.servo.value - self.move_amount
                        )
                    elif target_value > self.servo.value:
                        self.servo.value = min(
                            target_value, self.servo.value + self.move_amount
                        )

                    sleep(self.sleep_amount)


PartiallySmoothServo()
botafar.run()
