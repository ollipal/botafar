# Raspberry Pi tutorial

This tutorial tells how to remotely control LEDs and [servos](https://en.wikipedia.org/wiki/Servomotor) with a [Raspberry Pi](https://en.wikipedia.org/wiki/Raspberry_Pi) using botafar.

botafar does **not** require a lot of resources, so cheaper/older models such as [Raspberry Pi Zero](https://www.raspberrypi.com/products/raspberry-pi-zero/) should work well (For Raspberry Pi Zero I recommend Raspberry Pi OS Lite instead of Desktop version).

If you get confused about botafar during this tutorial, make sure to read [Get started](get_started) and [Basics](basics).

## OS and IDE installation

### Raspberry Pi OS

The first step is to install the operating system. I recommend using [Raspberry Pi OS Desktop](https://www.raspberrypi.com/documentation/computers/os.html#introduction) (or Raspberry Pi OS Lite for more experienced users), and installing it using [Raspberry Pi Imager](https://www.raspberrypi.com/software/) by following [these instructions](https://www.raspberrypi.com/documentation/computers/getting-started.html#installing-the-operating-system).

When you have your system running, it is a good idea to update the list of available software and upgrade the ones that are out of date by opening terminal and running

```
sudo apt update && sudo apt upgrade -y
```

### Writing and running code on Raspberry Pi OS

If you are not comfortable in writing code in terminal directly, there are many good options:

- [Thonny](https://thonny.org/) is simple and lightwieight IDE that comes pre-intalled on Raspberry Pi OS Desktop, [here is a simple video explaining how to use it](https://www.youtube.com/watch?v=GssM7hkwJrc) (This is the easiest of these options)
- You can install popular [Visual Studio Code](https://code.visualstudio.com/docs/setup/raspberry-pi) on Raspberry Pi (I recommend this only to the latest Raspberry Pis, it requires quite a lot of resources)
- If you have SSH connection working to your Pi and you'd like to use Visual Studio Code on your desktop to code remotely, you can use the [Remote SSH extension](https://cloudbytes.dev/snippets/develop-remotely-on-raspberry-pi-using-vscode-remote-ssh). (This can be hard to setup if you are not familiar with SSH)

## Python library installation

### botafar installation

First let's make sure you have [pip](https://en.wikipedia.org/wiki/Pip_(package_manager)) installed, which allows you to install Python packages.

```
sudo apt install python3-pip -y
```

Also, on you need to have [libSRTP](https://github.com/cisco/libsrtp) and other related network dependencies installed:

```
sudo apt install libnss3 libnspr4 libsrtp2-1 -y
```

Then, like in [get started](https://docs.botafar.com/get_started.html#botafar-setup), the installation should work by running

```
pip install --upgrade botafar
```

(Note that this command will take some time before anything gets printed to the terminal, in most cases it is working)

### GPIO library installation

Raspberry Pi has multiple good Python libraries for accessing hardware through its GPIO pins. In this tutorial we are going to use [gpiozero](https://gpiozero.readthedocs.io/en/stable/) library with [pigpio](http://abyz.me.uk/rpi/pigpio/) as a "[pin factory](https://gpiozero.readthedocs.io/en/stable/api_pins.html#module-gpiozero.pins.pigpio)". In my experience, this a good combination for creating bots because:

- gpiozero comes pre-installed with Raspberry Pi OS Desktop and Lite
- gpiozero is simpler to use than libraries like [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) or [pigpio](http://abyz.me.uk/rpi/pigpio/), especially for beginners
- gpiozero with pigpio "pin factory" allows using [hardware PWM](https://raspberrypi.stackexchange.com/a/100644), which means that servo motors do not stutter like when using Rpi.GPIO or gpiozero without pigpio pin factory

If you have a recent Raspberry Pi OS Desktop image installed, you should have gpiozero already indtalled.

To install pigpio daemon and its Python library, run

```
sudo apt install pigpio python3-pigpio -y
```

(More info [here](https://gpiozero.readthedocs.io/en/stable/installing.html) and [here](https://gpiozero.readthedocs.io/en/stable/remote_gpio.html#preparing-the-raspberry-pi))

The next step is to enable and start pigpio's daemon. This allows accessing hardware PWM.

```
sudo systemctl enable pigpiod --now
```

(More info [here](https://gpiozero.readthedocs.io/en/stable/remote_gpio.html#command-line-systemctl))

Now you should have gpiozero and pigpio installled, and pigpio daemon running.

## Blinking an LED remotely

1. Let's now follow the official [gpiozero LED tutorial](https://gpiozero.readthedocs.io/en/stable/recipes.html#led)'s wiring and connect an LED to GPIO pin 17 with a 330 ohm resistor, note that LED's shorter leg should be connected to ground pin:

![led](https://gpiozero.readthedocs.io/en/stable/_images/led_bb.svg)

(Image from the same tutorial, [licence](https://github.com/gpiozero/gpiozero/blob/master/LICENSE.rst)) [Raspberry Pi pins here](https://pinout.xyz).

To turn the LED on for one second, let's create and run a **main.py** file

```python
from gpiozero import LED
from time import sleep

led = LED(17)

print("led on")
led.on()
sleep(1)
print("led off")
led.off()
```

2. Similar to [get started](https://docs.botafar.com/get_started.html#botafar-setup), the steps to make this code remote controllable are:

- Import botafar
- Create a control, `Button` in this example, and bind a key from keyboard to it
- Use decorators (@-symbol) to select functions to call on user input
- Call `botafar.run()`

In this case we also create separate functions `led_on` and `led_off` and add `botafar.print` calls to make debugging easier.

```python
import botafar
from gpiozero import LED

b = botafar.Button("L")
led = LED(17)

@b.on_press
def led_on():
    botafar.print("led on")
    led.on()

@b.on_release
def led_off():
    botafar.print("led off")
    led.off()

botafar.run()
```

3. Execute the **main.py** file, and open the returned link in browser. **Most likely you want to open the link on other device, NOT on the Raspberry Pi itself**. Browser on Raspberry Pi tends to be too slow for a good experience.

```
$ python main.py

Bot running, connect at https://botafar.com/abcde-fghij-klmno
```

4. From the browser, press the **Try controls** -button. Now when you press and release <kbd>L</kbd> key from a keyboard or a touch screen, texts "led on" and "led off" get printed on terminal and the livestream, and the LED will blink.

```
$ python main.py

Bot running, connect at https://botafar.com/abcde-fghij-klmno
led on
led off
led on
led off
```

5. Choose a stream source from the browser. It can be a webcam, a phone or a screen share.

6. Give your bot a name and switch it to public

7. **The browser now shows a direct link to your bot you can share with anyone in the world!**

You are now ready to check [Advanced LED examples](https://docs.botafar.com/advanced#advanced-led-examples) if you want.

>Note: if you do not need the prints and just want to blink the LED, this simpler code has the same functionality

```python
import botafar
from gpiozero import LED

b = botafar.Button("L")
led = LED(17)
b.on_press(led.on)
b.on_release(led.off)
botafar.run()
```

## Moving a servo remotely

The process is very similar to [Blinking an LED remotely](#blinking-an-led-remotely) above.

1. Connect a small servo, such as [SG90](https://www.google.com/search?tbm=isch&as_q=sg90+servo) or [MG90s](https://www.google.com/search?tbm=isch&as_q=mg90s+servo), to Raspberry Pi. [Raspberry Pi pins here](https://pinout.xyz). (A larger servo [probably requires an external power supply](https://raspberrypi.stackexchange.com/a/33846) if you add load to the servo)

| Wire color    | Pin      |
|---------------|----------|
| Black/Brown   | Ground   |
| Red           | 5v power |
| Yellow/Orange | GPIO 17  |

To move the servo from left to right and middle, create and run a **main.py** file. Note the min/max pulse width values: these limits are from [Arduino Servo.h](https://github.com/arduino-libraries/Servo/blob/master/src/Servo.h#L82) library, which allow a full 180 degree movement with most hobby servos, but you should adjust them if your servo has different specs.

```python
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory # Optional, removes servo stutter!
from time import sleep

servo = Servo(
    17,
    pin_factory=PiGPIOFactory(),
    min_pulse_width=0.544/1000, # Adjust if needed
    max_pulse_width=2.4/1000, # Adjust if needed
)

print("servo value -1")
servo.value = -1
sleep(2)
print("servo value 1")
servo.value = 1
sleep(2)
print("servo value 0")
servo.value = 0
```

2. Similar to [Blinking an LED remotely](#blinking-an-led-remotely) above, the steps to make this code remote controllable are:
- Import botafar
- Create a control, `Joystick` in this example, and bind 4 keys from keyboard to it
- Use decorators (@-symbol) to select functions to call on user input
- Call `botafar.run()`

Let's also create wrapper angles to for each wanted position

```python
import botafar
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory # Optional, removes servo stutter!

j = botafar.Joystick("W","A","S","D")

servo = Servo(
    17,
    pin_factory=PiGPIOFactory(),
    min_pulse_width=0.544/1000, # Adjust if needed
    max_pulse_width=2.4/1000, # Adjust if needed
)

@j.on_left
def servo_left():
    botafar.print("servo value 1")
    servo.value = 1

@j.on_up_left
def servo_up_left():
    botafar.print("servo value 0.5")
    servo.value = 0.5

@j.on_up
@j.on_center
def servo_middle():
    botafar.print("servo value 0")
    servo.value = 0

@j.on_up_right
def servo_up_right():
    botafar.print("servo value -0.5")
    servo.value = -0.5

@j.on_right
def servo_right():
    botafar.print("servo value -1")
    servo.value = -1

# @j.on_down_left, @j.on_down, @j.on_down_right not used currently!

botafar.run()
```

3. Execute the **main.py** file, and open the returned link in browser. **Most likely you want to open the link on other device, NOT on the Raspberry Pi itself**. Browser on Raspberry Pi tends to be too slow for a good experience.

```
$ python main.py

Bot running, connect at https://botafar.com/abcde-fghij-klmno
```

4. From the browser, press the **Try controls** -button. Now when you press and release <kbd>W</kbd>, <kbd>A</kbd>, <kbd>S</kbd> and <kbd>D</kbd> keys from a keyboard or a touch screen, and servo values get printed on terminal and the livestream, and the servo should move.

```
$ python main.py

Bot running, connect at https://botafar.com/abcde-fghij-klmno
servo value -1
servo value 0
servo value 1
servo value 0.5
servo value 0
```

5. Choose a stream source from the browser. It can be a webcam, a phone or a screen share.

6. Give your bot a name and switch it to public

7. **The browser now shows a direct link to your bot you can share with anyone in the world!**

You are now ready to check [Advanced servo examples](https://docs.botafar.com/advanced#advanced-servo-examples) or project blueprints such as [Tank](https://docs.botafar.com/advanced#tank) or [RC car](https://docs.botafar.com/advanced#rc-car) if you want.

>Note: this simpler code has the same functionality

```python
import botafar
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory # Optional, removes servo stutter!

SERVO_VALUES = {
    "on_left":       1,
    "on_up_left":    0.5,
    "on_up":         0,
    "on_center":     0,
    "on_up_right":   -0.5,
    "on_right":      -1,
    "on_down_left":  None, # Not in use
    "on_down":       None, # Not in use
    "on_down_right": None, # Not in use
}

j = botafar.Joystick("W","A","S","D", diagonals=True)

servo = Servo(
    17,
    pin_factory=PiGPIOFactory(),
    min_pulse_width=0.544/1000, # Adjust if needed
    max_pulse_width=2.4/1000, # Adjust if needed
)

@j.on_any
def move_servo(event):
    servo_value = SERVO_VALUES[event.name]
    if servo_value is not None:
        botafar.print(f"servo value {servo_value}")
        servo.value = servo_value

botafar.run()
```