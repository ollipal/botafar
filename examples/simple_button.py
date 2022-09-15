"""
A simple example on how to react to key press
and release events with tb.Button
"""

import telebotties as tb

b = tb.Button("Q", alternative="C")

j = tb.Joystick("W", "A", "S", "D", alternative=["I", "J", "K", "L"])


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


""" @j.on_any
async def any(event):
    tb.print(f"ANY: {event}") """


@b.on_press
def press_callback():  # Access event: `def press_callback('event')`
    tb.print("Button pressed")


@b.on_release
def release_callback():  # Access event: `def release_callback('event')`
    tb.print("Button released")


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
