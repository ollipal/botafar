import botafar

"""
A simple example how to use botafar.Joystick
with diagonal directions
"""


j = botafar.Joystick("W", "A", "S", "D")


@j.on_center
def joystick_center():
    botafar.print("center")


@j.on_up
def joystick_up():
    botafar.print("up")


@j.on_left
def joystick_left():
    botafar.print("left")


@j.on_down
def joystick_down():
    botafar.print("down")


@j.on_right
def joystick_right():
    botafar.print("right")


# Diagonals:


@j.on_up_left
def joystick_up_left():
    botafar.print("up_left")


@j.on_down_left
def joystick_down_left():
    botafar.print("down_left")


@j.on_down_right
def joystick_down_right():
    botafar.print("down_right")


@j.on_up_right
def joystick_up_right():
    botafar.print("up_right")


botafar.run()
