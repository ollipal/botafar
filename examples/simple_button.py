"""
A simple example on how to react to key press
and release events with tb.Button
"""

import telebotties as tb

j = tb.Joystick("UP", "LEFT", "DOWN", "RIGHT", alt=["I", "J", "K", "L"])
b = tb.Button("SPACE", alt="C")

s = tb.Slider("U", "V")

s2 = tb.Slider("O", "E")


@s.on_any
def sleft(event):
    tb.print(event)


@s.on_up
def sright():
    tb.print("SRIGHT")


@j.on_center
def center():
    tb.print("CENTER")


@j.on_up
def up():
    tb.print("UP")


@j.on_left
def left():
    tb.print("LEFT")


@j.on_down
def down():
    tb.print("DOWN")


@j.on_right
def right():
    tb.print("RIGHT")


@j.on_up_left
def up_left():
    tb.print("UP LEFT")


"""
@j.on_down_left
def down_left():
    tb.print("DOWN LEFT")


@j.on_down_right
def down_right():
    tb.print("DOWN RIGHT")


@j.on_up_right
def up_right():
    tb.print("UP RIGHT")
 """

""" @j.on_any
async def any(event):
    tb.print(f"ANY: {event}") """


""" @b.on_press
def press_callback():  # Access event: `def press_callback('event')`
    tb.print("Button pressed")


@b.on_release
def release_callback():  # Access event: `def release_callback('event')`
    tb.print("Button released") """


tb.run()


"""
An alternative with a single callback:

import telebotties as tb

b = tb.Button("A")

@b.on_any
def release_button(event):
    if event.name == "press":
        print("Button pressed")
    elif event.name == "release":
        print("Button released")

tb.run()
"""
