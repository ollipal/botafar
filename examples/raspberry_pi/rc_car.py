from gpiozero import Motor, Servo
from gpiozero.pins.pigpio import (
    PiGPIOFactory,  # Optional, removes servo stutter!
)

import botafar

"""
Example how to create a RC car controllable by gpiozero.Servo, gpiozero.Motor
and botafar.Joystick. Motor sets the wheel spinning speed, servo steers
the front wheels.

Servo reference:
https://gpiozero.readthedocs.io/en/stable/api_output.html?highlight=Motor#gpiozero.Servo

Motor reference:
https://gpiozero.readthedocs.io/en/stable/api_output.html?highlight=Motor#gpiozero.Motor

The servo turning and motor speed changes could modified to work more
smoothly by using ideas from servo_smooth.py and tank_smooth.py.
"""

SERVO_GPIO_PIN = 17
MOTOR_FORWARD_GPIO_PIN = 4
MOTOR_BACKWARD_GPIO_PIN = 14

SERVO_VALUES = {
    "on_left": 1,
    "on_up_left": 0.5,
    "on_down_left": 0.5,
    "on_up": 0,
    "on_down": 0,
    "on_center": 0,
    "on_up_right": -0.5,
    "on_down_right": -0.5,
    "on_right": -1,
}

MOTOR_VALUES = {
    "on_up": 1,
    "on_up_right": 1,
    "on_up_left": 1,
    "on_right": 1,
    "on_left": 1,
    "on_center": 0,
    "on_down": -1,
    "on_down_right": -1,
    "on_down_left": -1,
}

j = botafar.Joystick(
    "W", "A", "S", "D", alt=["UP", "LEFT", "DOWN", "RIGHT"], diagonals=True
)


# Can be changed to SmoothServo, PartiallySmoothServo
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


# Can be changed to SmoothMotor from tank_smooth.py
class ImmediateMotor:
    def __init__(self):
        self.motor = Motor(
            forward=MOTOR_FORWARD_GPIO_PIN,
            backward=MOTOR_BACKWARD_GPIO_PIN,
        )

    @j.on_any
    def drive(self, event):
        motor_value = MOTOR_VALUES.get(event.name)
        if motor_value is not None:
            botafar.print(f"motor value {motor_value}")
            self.motor.value = motor_value


ImmediateServo()
ImmediateMotor()
botafar.run()
