import botafar

"""
A simple example how to use botrafar.stop() and botafar.exit()
"""


@botafar.on_time(5)
def after_5_seconds():
    botafar.print("5 seconds passed, stopping or exiting")

    # Uncomment to try exit() instead of stop
    # botafar.exit()

    botafar.stop()


b = botafar.Button("SPACE")  # This enables remote controlling
botafar.run()
