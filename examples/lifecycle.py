import botafar

"""
A simple example how to use the main lifecycle
functions: on_prepare, on_start and on_stop
"""


# This runs before each remote control
@botafar.on_prepare
def lifecycle_prepare():
    botafar.print("prepare")


# This runs when remote controlling starts
@botafar.on_start
def lifecycle_start():
    botafar.print("start")


# This runs when remote controlling stops
@botafar.on_stop
def lifecycle_stop():
    botafar.print("stop")


b = botafar.Button("SPACE")  # This enables remote controlling
botafar.run()
