# Advanced

This chapter goes through some advanced botafar features not seen in [Get started](get_started) and [Basics](basics) as well as more advanced hardware examples than in [Arduino tutorial](arduino) and [Raspberry Pi tutorial](raspi).

## Advanced LED examples

### Toggling LED

An example that shows how to toggle an LED

```python
from gpiozero import LED
import botafar

b = botafar.Button("L", alt="SPACE")
led = LED(17)
b.on_press(led.toggle)
botafar.on_prepare(led.off) # Turn off between controls
botafar.run()
```

## Advanced servo examples

These servo examples could be used for example steering a RC car. Different movement styles would provide a different driving experience.

These examples leverage `Event.is_active` property. This has a value of `True` or `False` depending on is the event the latest one or not.

### Immediate servo

Servo example with a custom class, immediate movement to the target value.

```python
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory  # Optional, removes servo stutter!
import botafar

SERVO_GPIO_PIN = 17
SERVO_VALUES = {
    "on_left":       1,
    "on_up_left":    0.5,
    "on_up":         0,
    "on_center":     0,
    "on_up_right":   -0.5,
    "on_right":      -1,
}

j = botafar.Joystick("W", "A", "S", "D", alt=["UP", "LEFT", "DOWN", "RIGHT"], diagonals=True)

class ImmediateServo:
    def __init__(self):
        self.servo = Servo(
            SERVO_GPIO_PIN,
            pin_factory=PiGPIOFactory(),
            min_pulse_width=0.544 / 1000,  # Adjust if needed
            max_pulse_width=2.4 / 1000,  # Adjust if needed
        )

    @j.on_any
    def move_servo(self, event):
        servo_value = SERVO_VALUES.get(event.name)
        if servo_value is not None:
            botafar.print(f"servo value {servo_value}")
            self.servo.value = servo_value

ImmediateServo()
botafar.run()
```

### Smooth servo

Servo example with a custom class, smooth movement to the target value.

Adjust `SERVO_STEPS` and `SERVO_UPDATE_FREQ` to alter movement speed and smoothness.

```python
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory  # Optional, removes servo stutter!
from time import sleep
from threading import Lock
import botafar

SERVO_GPIO_PIN = 17
SERVO_STEPS = 40
SERVO_UPDATE_FREQ = 25
SERVO_VALUES = {
    "on_left":       1,
    "on_up_left":    0.5,
    "on_up":         0,
    "on_center":     0,
    "on_up_right":   -0.5,
    "on_right":      -1,
}

j = botafar.Joystick("W", "A", "S", "D", alt=["UP", "LEFT", "DOWN", "RIGHT"], diagonals=True)

class SmoothServo:
    def __init__(self):
        self.servo = Servo(
            SERVO_GPIO_PIN,
            pin_factory=PiGPIOFactory(),
            min_pulse_width=0.544 / 1000,  # Adjust if needed
            max_pulse_width=2.4 / 1000,  # Adjust if needed
        )
        self.target_value = 0
        self.sleep_amount = 1 / SERVO_UPDATE_FREQ
        self.move_amount = 2 / SERVO_STEPS
        self.lock = Lock() # Fixes concurrency issues

    @j.on_any
    def move_servo(self, event):
        with self.lock:
            target_value = SERVO_VALUES.get(event.name)
            if target_value is not None:
                botafar.print(f"servo target value {target_value}")
                while event.is_active and target_value != self.servo.value:

                    if target_value < self.servo.value:
                        self.servo.value = max(target_value, self.servo.value - self.move_amount)
                    elif target_value > self.servo.value:
                        self.servo.value = min(target_value, self.servo.value + self.move_amount)

                    sleep(self.sleep_amount)

SmoothServo()
botafar.run()
```

### Partially smooth servo

Servo example with a custom class, smooth movement to the target value, immediate return to center.

Adjust `SERVO_STEPS` and `SERVO_UPDATE_FREQ` to alter movement speed and smoothness.

```python
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory  # Optional, removes servo stutter!
from time import sleep
from threading import Lock
import botafar

SERVO_GPIO_PIN = 17
SERVO_STEPS = 40
SERVO_UPDATE_FREQ = 25
SERVO_VALUES = {
    "on_left":       1,
    "on_up_left":    0.5,
    "on_up":         0,
    "on_center":     0,
    "on_up_right":   -0.5,
    "on_right":      -1,
}

j = botafar.Joystick("W", "A", "S", "D", alt=["UP", "LEFT", "DOWN", "RIGHT"], diagonals=True)

class PartiallySmoothServo:
    def __init__(self):
        self.servo = Servo(
            SERVO_GPIO_PIN,
            pin_factory=PiGPIOFactory(),
            min_pulse_width=0.544 / 1000,  # Adjust if needed
            max_pulse_width=2.4 / 1000,  # Adjust if needed
        )
        self.target_value = 0
        self.sleep_amount = 1 / SERVO_UPDATE_FREQ
        self.move_amount = 2 / SERVO_STEPS
        self.lock = Lock() # Fixes concurrency issues

    @j.on_any
    def move_servo(self, event):
        with self.lock:
            target_value = SERVO_VALUES.get(event.name)
            if target_value is not None:
                botafar.print(f"servo target value {target_value}")
                while event.is_active and target_value != self.servo.value:

                    if target_value == 0:
                        self.servo.value = target_value
                    elif target_value < self.servo.value:
                        self.servo.value = max(target_value, self.servo.value - self.move_amount)
                    elif target_value > self.servo.value:
                        self.servo.value = min(target_value, self.servo.value + self.move_amount)

                    sleep(self.sleep_amount)

PartiallySmoothServo()
botafar.run()
```

## Other examples

### Not spammable relay

Example how to connect a relay to gpiozero [OutputDevice](https://gpiozero.readthedocs.io/en/stable/api_output.html?highlight=OutputDevice#outputdevice), and prevent players from spamming it too fast.

```python
from gpiozero import OutputDevice
import botafar
from time import sleep

b = botafar.Button("SPACE")

RELAY_GPIO_PIN = 17
RELAY_TIME_ON = 0.1
RELAY_TIME_OFF = 2

class NotSpammableRelay:
    def __init__(self):
        self.relay = OutputDevice(RELAY_GPIO_PIN, active_high=True, initial_value=False)
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
```

## Project blueprints

Here is code for some typical bot types, you can use as starting points for your projects.

### Tank

#### Basic tank

Example how to create a tank controllable by two instances of gpiozero [Motor](https://gpiozero.readthedocs.io/en/stable/api_output.html?highlight=Motor#gpiozero.Motor) and botafar.Joystick. This example works if you have two independently controllable wheels, left and right one.

Tank wiring example from gpiozero [Robot](https://gpiozero.readthedocs.io/en/stable/recipes.html#robot) tutorial using SN754410 motor driver, [image licence](https://github.com/gpiozero/gpiozero/blob/master/LICENSE.rst).

![tank wiring](https://gpiozero.readthedocs.io/en/stable/_images/robot_bb.svg)

```python
from gpiozero import Motor
import botafar

LEFT_MOTOR_FORWARD_GPIO_PIN = 4
LEFT_MOTOR_BACKWARD_GPIO_PIN = 14
RIGHT_MOTOR_FORWARD_GPIO_PIN = 17
RIGHT_MOTOR_BACKWARD_GPIO_PIN = 18

MOTOR_VALUES = {
    "on_center":     ( 0.0, 0.0),
    "on_up":         ( 1.0, 1.0),
    "on_up_left":    ( 0.5, 1.0),
    "on_left":       (-0.5, 0.5),
    "on_down_left":  (-0.5,-1.0),
    "on_down":       (-1.0,-1.0),
    "on_down_right": (-1.0,-0.5),
    "on_right":      ( 0.5,-0.5),
    "on_up_right":   ( 1.0, 0.5),
}

j = botafar.Joystick("W", "A", "S", "D", alt=["UP", "LEFT", "DOWN", "RIGHT"], diagonals=True)

left_motor = Motor(
    forward=LEFT_MOTOR_FORWARD_GPIO_PIN,
    backward=LEFT_MOTOR_BACKWARD_GPIO_PIN,
)

right_motor = Motor(
    forward=RIGHT_MOTOR_FORWARD_GPIO_PIN,
    backward=RIGHT_MOTOR_BACKWARD_GPIO_PIN,
)

@j.on_any
def drive_tank(event):
    left_value, right_value = MOTOR_VALUES[event.name]
    left_motor.value = left_value
    right_motor.value = right_value

botafar.run()
```

#### Smooth tank

This is a similar example to the previous one, but this changes motor speeds smoothly.

Change `MOTOR_STEPS` and `MOTOR_UPDATE_FREQ` to change how tank accelerates.

```python
from threading import Lock
from time import sleep
from gpiozero import Motor
import botafar

LEFT_MOTOR_FORWARD_GPIO_PIN = 4
LEFT_MOTOR_BACKWARD_GPIO_PIN = 14
RIGHT_MOTOR_FORWARD_GPIO_PIN = 17
RIGHT_MOTOR_BACKWARD_GPIO_PIN = 18
MOTOR_STEPS = 40  # How many distinct motor speeds
MOTOR_UPDATE_FREQ = 25  # How many speed updates per second

LEFT_MOTOR_VALUES = {
    "on_center":      0.0,
    "on_up":          1.0,
    "on_up_left":     0.5,
    "on_left":       -0.5,
    "on_down_left":  -0.5,
    "on_down":       -1.0,
    "on_down_right": -1.0,
    "on_right":       0.5,
    "on_up_right":    1.0,
}

RIGHT_MOTOR_VALUES = {
    "on_center":      0.0,
    "on_up":          1.0,
    "on_up_left":     1.0,
    "on_left":        0.5,
    "on_down_left":  -1.0,
    "on_down":       -1.0,
    "on_down_right": -0.5,
    "on_right":      -0.5,
    "on_up_right":    0.5,
}

j = botafar.Joystick(
    "W", "A", "S", "D", alt=["UP", "LEFT", "DOWN", "RIGHT"], diagonals=True
)

class SmoothMotor:
    def __init__(self, forward_pin, backward_pin, values):
        self.motor = Motor(
            forward=forward_pin,
            backward=backward_pin,
        )
        self.values = values
        self.target_value = 0
        self.sleep_amount = 1 / MOTOR_UPDATE_FREQ
        self.change_amount = 2 / MOTOR_STEPS
        self.lock = Lock()  # Fixes concurrency issues

    @j.on_any
    def drive(self, event):
        with self.lock:
            target_value = self.values[event.name]
            botafar.print(f"motor target value {target_value}")
            while event.is_active and target_value != self.motor.value:

                if target_value < self.motor.value:
                    self.motor.value = max(
                        target_value, self.motor.value - self.change_amount
                    )
                elif target_value > self.motor.value:
                    self.motor.value = min(
                        target_value, self.motor.value + self.change_amount
                    )

                sleep(self.sleep_amount)


SmoothMotor(
    LEFT_MOTOR_FORWARD_GPIO_PIN,
    LEFT_MOTOR_BACKWARD_GPIO_PIN,
    LEFT_MOTOR_VALUES,
)
SmoothMotor(
    RIGHT_MOTOR_FORWARD_GPIO_PIN,
    RIGHT_MOTOR_BACKWARD_GPIO_PIN,
    RIGHT_MOTOR_VALUES,
)
botafar.run()
```

### RC car

Example how to create a RC car controllable by gpiozero [Servo](https://gpiozero.readthedocs.io/en/stable/api_output.html?highlight=Motor#gpiozero.Servo), gpiozero [Motor](https://gpiozero.readthedocs.io/en/stable/api_output.html?highlight=Motor#gpiozero.Motor) and botafar.Joystick. Motor sets the wheel spinning speed, servo steers the front wheels.

The servo turning and motor speed changes could modified to work more
smoothly by using ideas from [Smooth servo](#smooth-servo) and  [Smooth tank](#smooth-tank).

```python
from gpiozero import Servo, Motor
from gpiozero.pins.pigpio import PiGPIOFactory # Optional, removes servo stutter!
import botafar

SERVO_GPIO_PIN = 17
MOTOR_FORWARD_GPIO_PIN = 4
MOTOR_BACKWARD_GPIO_PIN = 14

SERVO_VALUES = {
    "on_left":       1,
    "on_up_left":    0.5,
    "on_down_left":  0.5,
    "on_up":         0,
    "on_down":       0,
    "on_center":     0,
    "on_up_right":   -0.5,
    "on_down_right": -0.5,
    "on_right":      -1,
}

MOTOR_VALUES = {
    "on_up":         1,
    "on_up_right":   1,
    "on_up_left":    1,
    "on_right":      1,
    "on_left":       1,
    "on_center":     0,
    "on_down":       -1,
    "on_down_right": -1,
    "on_down_left":  -1,
}

j = botafar.Joystick("W", "A", "S", "D", alt=["UP", "LEFT", "DOWN", "RIGHT"], diagonals=True)

# Can be changed to SmoothServo, PartiallySmoothServo
class ImmediateServo:
    def __init__(self):
        self.servo = Servo(
            SERVO_GPIO_PIN,
            pin_factory=PiGPIOFactory(),
            min_pulse_width=0.544 / 1000,  # Adjust if needed
            max_pulse_width=2.4 / 1000,  # Adjust if needed
        )

    @j.on_any
    def move_servo(self, event):
        servo_value = SERVO_VALUES.get(event.name)
        if servo_value is not None:
            botafar.print(f"servo value {servo_value}")
            self.servo.value = servo_value


# Can be changed to SmoothMotor from Smooth tank example
class ImmediateMotor:
    def __init__(self):
        self.motor = Motor(
            forward=MOTOR_FORWARD_GPIO_PIN,
            backward=MOTOR_BACKWARD_GPIO_PIN,
        )

    @j.on_any
    def drive(self, event):
        motor_value = MOTOR_VALUES.get(event.name)
        if motor_value is not None:
            botafar.print(f"motor value {motor_value}")
            self.motor.value = motor_value


ImmediateServo()
ImmediateMotor()
botafar.run()
```

## Coming soon

- Holding keys, and related topics (using Event)
- Detecting who is controlling (using Event)
- Owner only controls (2 ways)
- Botafar cli
