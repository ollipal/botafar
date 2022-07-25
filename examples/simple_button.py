"""
A simple example on how to react to key press
and release events with tb.Button
"""

import telebotties as tb

b = tb.Button("A")


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
