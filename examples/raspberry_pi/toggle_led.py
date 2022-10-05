from gpiozero import LED

import botafar

"""
An example that shows how to toggle an LED
"""

b = botafar.Button("L", alt="SPACE")
led = LED(17)
b.on_press(led.toggle)
botafar.on_prepare(led.off)  # Turn off between controls
botafar.run()
