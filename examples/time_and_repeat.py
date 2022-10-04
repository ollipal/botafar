import botafar

"""
A simple example how to use on_time, on_repeat and botrafar.time()
"""


# Repeats callback with one second in between calls
# botafar.time() is used here to get the current time
@botafar.on_repeat(sleep=1)
def once_second():
    botafar.print(f"repeating {botafar.time()}")


# Triggers after 3 seconds, if player has not disconnected before
@botafar.on_time(3)
def after_3_seconds():
    botafar.print("3 seconds passed")


# Triggers after 5 and 8 seconds, if player has not disconnected before
# Note the optional 'time' parameter that gets filled automatically
@botafar.on_time(5, 8)
def after_5_and_8_seconds(time):
    botafar.print(f"{time} seconds passed")


# Countdown demo by unpacking a range
@botafar.on_time(*range(10, 15))
def countdown(time):
    botafar.print(f"Time left {15 - time}")


b = botafar.Button("SPACE")  # This enables remote controlling
botafar.run()
