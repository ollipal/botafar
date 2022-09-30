# Basics

This section contains some basic concepts of botafar library.

Most likely you should read this before going through [Arduino](arduino) or [Raspberry Pi](raspi) tutorials (or they might be a bit confusing).

## Project status

Botafar is still under development. The current aim is to make creating remote controllable bots a simple, enjoyable and bug free experience. The communication about project happens on [GitHub discussions](https://github.com/ollipal/botafar/discussions).

If you got stuck or need help with botafar library or website, please write to [Q&A](https://github.com/ollipal/botafar/discussions/categories/q-a).

If you experience bugs on botafar library or website, please write about it to [Bug Tracking](https://github.com/ollipal/botafar/discussions/categories/bug-tracking), even if you are not sure if its a bug or not. Alternatively you can raise [an issue](https://github.com/ollipal/botafar/issues) on purely library related matters (or even create [a pull request](https://github.com/ollipal/botafar/pulls) if you think you have the bug figured out).

If you want to tell about your creations, get involved or anything else, write about it to [General](https://github.com/ollipal/botafar/discussions/categories/general). There is also a separate category for new [Ideas](https://github.com/ollipal/botafar/discussions/categories/q-a).

## run()

All botafar bots require a one `botafar.run()` call after the callbacks have been registered.

## print()

If you have prints you want to show to the user

```python
print("You won!")
```

You can print it directly to the livestream by using `botafar.print`

```python
botafar.print("You won!")
```

If you want to show all prints from a file to a user, you can override the default print

```python
import botafar
from botafar import print

print("You won!")
```

## Available controls

_Controls_ bind one or more keyboard keys. When those keys are pressed on a keyboard or touch screen, they change the contorl's state which will trigger callbacks.

Available keyboard keys are <kbd>A-Z</kbd>, <kbd>UP</kbd>, <kbd>LEFT</kbd>, <kbd>DOWN</kbd>, <kbd>RIGHT</kbd> and <kbd>SPACE</kbd>

### Button

The simplest control is `Button` binds one key. It has `on_press` and `on_release` states.

```python
b = botafar.Button("SPACE")

@b.on_press
def press():
    botafar.print("press")

@b.on_release
def press():
    botafar.print("release")
```

### Slider

`Slider` bind two keys and it has two variations, horizontal and vertical. These variations are automatically detected based on the callback functions registered.

Horizontal slider has three states: `on_left`, `on_right` and `on_center`.

Vertical slider states are: `on_up`, `on_down` and `on_center`.

```python
s = botafar.Slider("J","L")

@s.on_center
def center():
    botafar.print("center")

# A horizontal Slider:
@s.on_left
def left():
    botafar.print("left")

@s.on_right
def right():
    botafar.print("right")

# If you want a vertical Slider, use @s.on_up/@s.on_down instead
```

### Joystick

`Joystick` bind four keys and it has two variations, without diagonals and with diagonals. In keyboard it means having callbacks for certain combinations of keys, such as pressing <kbd>W</kbd> and <kbd>A</kbd> at the same time. On mobile touch screen this means the area between <kbd>W</kbd> and <kbd>A</kbd> keys.

These variations are automatically detected based on the callback functions registered.

Joystick without diagonals has 5 callbacks: `on_up`, `on_left`, `on_down`, `on_right` and `on_center`.

Joystick with diagonals has 4 _additional_ callbacks: `on_up_left`, `on_down_left`, `on_down_right`, `on_up_right`.

```python
j = botafar.Joystick("W","A","S","D")

@j.on_center
def center():
    botafar.print("center")

@j.on_up
def up():
    botafar.print("up")

@j.on_left
def left():
    botafar.print("left")

@j.on_down
def down():
    botafar.print("down")

@j.on_right
def right():
    botafar.print("right")

# Diagonals:

@j.on_up_left
def up_left():
    botafar.print("up_left")

@j.on_down_left
def down_left():
    botafar.print("down_left")

@j.on_down_right
def down_right():
    botafar.print("down_right")

@j.on_up_right
def up_right():
    botafar.print("up_right")
```

The example above shows that having this many control states results in quite many rows callback functions. Later we see how this can be simplified in many cases with [on_any](https://docs.botafar.com/basics.html#on-any) or by [stacking callbacks](https://docs.botafar.com/basics.html#stacked-callbacks).

## Common control features

### Event

`Event` represents a single state change for controls. It allows you write more complex bot logic as well as more readable code in many cases (examples come later)

It can be accessed by adding a parameter called `event` as the first parameter to the callback methods

```python
b = botafar.Button("SPACE")

@b.on_press
def press(event):
    botafar.print(event)
```

This prints:

```
Event(name='on_press', is_active=True, sender='owner', time=-1)
```

(on [class method callbacks](https://docs.botafar.com/basics.html#class-method-callbacks), the event parameter comes after "self")

### on_any

In addition to the regular state callbacks, all controls have a special callback `on_any` that triggers on all state changes, and **requires** an event parameter. In many cases this allows making more readable code.

```python
TANK_MOTOR_SPEEDS = {
    "on_center":     ( 0.0, 0.0)
    "on_up":         ( 1.0, 1.0),
    "on_up_left":    ( 0.5, 1.0),
    "on_left":       ( 0.0, 1.0),
    "on_down_left":  (-0.5,-1.0),
    "on_down":       (-1.0,-1.0),
    "on_down_right": (-1.0,-0.5),
    "on_right":      ( 1.0, 0.0),
    "on_up_right":   ( 1.0, 0.5),
}

j = botafar.Joystick("W","A","S","D", diagonals=True)

@j.on_any
def any(event):
    left_speed, right_speed = TANK_MOTOR_SPEED[event.name]
    # Do something with the speeds
```

### alt keys

If you want to have multiple keys triggering the same callbacks, you can use `alt` parameter.

All controls have a `alt` parameter. For Button, the type is string, for Slider and Joystick, it is a list of strings.

```python
b = botafar.Button("SPACE", alt="C")
s = botafar.Slider("J","L", alt=["U","O"])
j = botafar.Joystick("W","A","S","D", alt=["UP","LEFT","DOWN","RIGHT"])
```

## Callbacks

So far we've seen only individual callbacks registered to functions.

```python
import botafar

b = botafar.Button("A")

@b.on_press
def press():
    botafar.print("press")

botafar.run()
```

But they can be used in many more situations.

### Class method callbacks

**You can use class methods in addition to functions as callbacks!** This can make your code more readable. But remember to create at least one class instance.

```python
import botafar

b = botafar.Button("A")

class Bot:
    def __init__(self, name):
        self.name = name

    @b.on_press
    def press(self):
        botafar.print(self.name + " pressed")

bot = Bot("Bob") # Important
botafar.run()
```

### Async callbacks

botafar supports Python's [asyncio](https://docs.python.org/3/library/asyncio.html), if you need it.

```python
@b.on_press
async def press():
    botafar.print("press")
```

### Multiple callbacks

You can have multiple callbacks tied to the same state change.

```python
@b.on_press
def press():
    botafar.print("press 1")

@b.on_press
def press():
    botafar.print("press 2")
```

### Stacked callbacks

You can "stack" callbacks from multiple controls to the same function.

```python
b = botafar.Button("A")
s = botafar.Slider("I","K")

@b.on_press
@s.on_up
@s.on_down
def press_or_up_or_down():
    botafar.print("press or up or down")
```

### Callbacks without decorator

Instead of creating redundant functions for wrapping other functions

```python
import botafar
from some_package import jump # Example

b = botafar.Button("A")

@b.on_press
def press():
    jump()
```

you can also register them directly

```python
import botafar
from some_package import jump # Example

b = botafar.Button("A")

b.on_press(jump)
```
