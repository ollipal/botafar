from threading import Lock
from time import sleep

from gpiozero import Motor

import botafar

"""
Example how to create a tank controllable by two instances of gpiozero.Motor
and botafar.Joystick. This example works if you have two independently
controllable wheels, left and right one.

This example changes motor speeds smoothly. Check tank_basic.py for
a simpler example.

Change MOTOR_STEPS and MOTOR_UPDATE_FREQ to change how tank accelerates.

Motor reference:
https://gpiozero.readthedocs.io/en/stable/api_output.html?highlight=Motor#gpiozero.Motor
"""

LEFT_MOTOR_FORWARD_GPIO_PIN = 4
LEFT_MOTOR_BACKWARD_GPIO_PIN = 14
RIGHT_MOTOR_FORWARD_GPIO_PIN = 17
RIGHT_MOTOR_BACKWARD_GPIO_PIN = 18
MOTOR_STEPS = 40  # How many distinct motor speeds
MOTOR_UPDATE_FREQ = 25  # How many speed updates per second

LEFT_MOTOR_VALUES = {
    "on_center": 0.0,
    "on_up": 1.0,
    "on_up_left": 0.5,
    "on_left": -0.5,
    "on_down_left": -0.5,
    "on_down": -1.0,
    "on_down_right": -1.0,
    "on_right": 0.5,
    "on_up_right": 1.0,
}

RIGHT_MOTOR_VALUES = {
    "on_center": 0.0,
    "on_up": 1.0,
    "on_up_left": 1.0,
    "on_left": 0.5,
    "on_down_left": -1.0,
    "on_down": -1.0,
    "on_down_right": -0.5,
    "on_right": -0.5,
    "on_up_right": 0.5,
}

j = botafar.Joystick(
    "W", "A", "S", "D", alt=["UP", "LEFT", "DOWN", "RIGHT"], diagonals=True
)


class SmoothMotor:
    def __init__(self, forward_pin, backward_pin, values):
        self.motor = Motor(
            forward=forward_pin,
            backward=backward_pin,
        )
        self.values = values
        self.target_value = 0
        self.sleep_amount = 1 / MOTOR_UPDATE_FREQ
        self.change_amount = 2 / MOTOR_STEPS
        self.lock = Lock()  # Fixes concurrency issues

    @j.on_any
    def drive(self, event):
        with self.lock:
            target_value = self.values[event.name]
            botafar.print(f"motor target value {target_value}")
            while event.is_active and target_value != self.motor.value:

                if target_value < self.motor.value:
                    self.motor.value = max(
                        target_value, self.motor.value - self.change_amount
                    )
                elif target_value > self.motor.value:
                    self.motor.value = min(
                        target_value, self.motor.value + self.change_amount
                    )

                sleep(self.sleep_amount)


SmoothMotor(
    LEFT_MOTOR_FORWARD_GPIO_PIN,
    LEFT_MOTOR_BACKWARD_GPIO_PIN,
    LEFT_MOTOR_VALUES,
)
SmoothMotor(
    RIGHT_MOTOR_FORWARD_GPIO_PIN,
    RIGHT_MOTOR_BACKWARD_GPIO_PIN,
    RIGHT_MOTOR_VALUES,
)
botafar.run()
