import botafar

"""
A simple example how to use botafar.Joystick
without diagonal directions
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


botafar.run()
