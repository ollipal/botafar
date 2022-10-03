import botafar

"""
A simple example how to use botafar.Joystick
without diagonal directions
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


botafar.run()
