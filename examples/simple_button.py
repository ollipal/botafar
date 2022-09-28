"""
A simple example on how to react to key press
and release events with botafar.Button
"""


import botafar

b = botafar.Button("SPACE", alt="C")
j = botafar.Joystick("W", "A", "S", "D", alt=["I", "J", "K", "L"])

s = botafar.Slider("U", "V")

s2 = botafar.Slider("O", "E")


@s.on_any
def sleft(event):
    botafar.print(event)


@s.on_up
def sright():
    botafar.print("SRIGHT")


@j.on_center
def center():
    botafar.print("CENTER")


@j.on_up
def up():
    botafar.print("UP")


@j.on_left
def left():
    botafar.print("LEFT")


@j.on_down
def down():
    botafar.print("DOWN")


@j.on_right
def right():
    botafar.print("RIGHT")


@j.on_up_left
def up_left():
    botafar.print("UP LEFT")


@j.on_down_left
def down_left():
    botafar.print("DOWN LEFT")


@j.on_down_right
def down_right():
    botafar.print("DOWN RIGHT")


@j.on_up_right
def up_right():
    botafar.print("UP RIGHT")


@j.on_any
async def any(event):
    botafar.print(f"ANY: {event}")


@b.on_press
def press_callback(event):  # Access event: `def press_callback('event')`
    botafar.print(event)


@b.on_release
def release_callback():  # Access event: `def release_callback('event')`
    botafar.print("Button released")


botafar.run()


"""
An alternative with a single callback:

import botafar as botafar

b = botafar.Button("A")

@b.on_any
def release_button(event):
    if event.name == "press":
        print("Button pressed")
    elif event.name == "release":
        print("Button released")

botafar.run()
"""
