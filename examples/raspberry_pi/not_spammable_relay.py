from time import sleep

from gpiozero import OutputDevice

import botafar

"""
Example how to connect a relay to gpiozero.OutputDevice, and prevent players
from spamming it too fast.

OutputDevice reference:
https://gpiozero.readthedocs.io/en/stable/api_output.html?highlight=OutputDevice#outputdevice
"""

b = botafar.Button("SPACE")

RELAY_GPIO_PIN = 17
RELAY_TIME_ON = 0.1
RELAY_TIME_OFF = 2


class NotSpammableRelay:
    def __init__(self):
        self.relay = OutputDevice(
            RELAY_GPIO_PIN, active_high=True, initial_value=False
        )
        self.cycling = False

    @b.on_press
    def cycle_relay(self):
        if self.cycling:
            botafar.print("Spamming relay too fast, skipping")
            return

        self.cycling = True
        self.relay.on()
        sleep(RELAY_TIME_ON)
        self.relay.off()
        sleep(RELAY_TIME_OFF)
        self.cycling = False


NotSpammableRelay()
botafar.run()
