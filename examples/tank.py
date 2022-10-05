from gpiozero import Motor

import botafar

"""
Example how to create a tank controllable by two instances of gpiozero.Motor
and botafar.Joystick. This example works if you have two independently
controllable wheels, left and right one.

Motor API:
https://gpiozero.readthedocs.io/en/stable/api_output.html?highlight=Motor#gpiozero.Motor

The motor speed changes could modified to work more
smoothly by using ideas from servo_smooth.py or servo_partially_smooth.py.
"""

LEFT_MOTOR_FORWARD_GPIO_PIN = 4
LEFT_MOTOR_BACKWARD_GPIO_PIN = 14
RIGHT_MOTOR_FORWARD_GPIO_PIN = 4
RIGHT_MOTOR_BACKWARD_GPIO_PIN = 14

MOTOR_VALUES = {
    "on_center": (0.0, 0.0),
    "on_up": (1.0, 1.0),
    "on_up_left": (0.5, 1.0),
    "on_left": (0.0, 1.0),
    "on_down_left": (-0.5, -1.0),
    "on_down": (-1.0, -1.0),
    "on_down_right": (-1.0, -0.5),
    "on_right": (1.0, 0.0),
    "on_up_right": (1.0, 0.5),
}

j = botafar.Joystick(
    "W", "A", "S", "D", alt=["UP", "LEFT", "DOWN", "RIGHT"], diagonals=True
)

left_motor = Motor(
    forward=LEFT_MOTOR_FORWARD_GPIO_PIN,
    backward=LEFT_MOTOR_BACKWARD_GPIO_PIN,
)

right_motor = Motor(
    forward=RIGHT_MOTOR_FORWARD_GPIO_PIN,
    backward=RIGHT_MOTOR_BACKWARD_GPIO_PIN,
)


@j.on_any
def drive_tank(event):
    left_value, right_value = MOTOR_VALUES[event.name]
    left_motor.value = left_value
    right_motor.value = right_value


botafar.run()
