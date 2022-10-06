import botafar

"""
A simple example how to use botafar.Slider
"""


sh = botafar.Slider("J", "L")  # A horizontal Slider


@sh.on_center
def horizontal_center():
    botafar.print("horizontal center")


@sh.on_left
def left():
    botafar.print("left")


@sh.on_right
def right():
    botafar.print("right")


sv = botafar.Slider("I", "K")  # A vertical Slider


@sv.on_center
def vertical_center():
    botafar.print("vertical center")


@sv.on_up
def up():
    botafar.print("up")


@sv.on_down
def down():
    botafar.print("down")


botafar.run()
