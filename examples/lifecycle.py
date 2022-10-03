import botafar

"""
A simple example how to react to key press
and release events with botafar.Button
"""

b = botafar.Button("SPACE")


@botafar.on_start
def start():
    botafar.print("start")


@b.on_press
def button_press():
    botafar.print("press")


@b.on_release
def button_release():
    botafar.print("release")


botafar.run()
