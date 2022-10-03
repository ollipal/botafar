import botafar

"""
A simple example how to use botafar.Joystick
with diagonal directions
"""


j = botafar.Joystick("W", "A", "S", "D")


@j.on_center
def center():
    botafar.print("center")


@j.on_up
def up():
    botafar.print("up")


@j.on_left
def left():
    botafar.print("left")


@j.on_down
def down():
    botafar.print("down")


@j.on_right
def right():
    botafar.print("right")


# Diagonals:


@j.on_up_left
def up_left():
    botafar.print("up_left")


@j.on_down_left
def down_left():
    botafar.print("down_left")


@j.on_down_right
def down_right():
    botafar.print("down_right")


@j.on_up_right
def up_right():
    botafar.print("up_right")


botafar.run()
