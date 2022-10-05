from gpiozero import LED

import botafar

"""
An example that shows how to enable toggling a LED
"""


b = botafar.Button("L", alt="SPACE")


class LedToggler:
    def __init__(self):
        self.led = LED(17)
        self.is_on = False

    def led_on(self):
        botafar.print("led on")
        self.led.on()
        self.is_on = True

    def led_off(self):
        botafar.print("led off")
        self.led.off()
        self.is_on = False

    @b.on_press
    def toggle_led(self):
        if self.is_on:
            self.led_off()
        else:
            self.led_on()


led_toggler = LedToggler()

# Turn off between controls
botafar.on_prepare(led_toggler.led_off)

botafar.run()
