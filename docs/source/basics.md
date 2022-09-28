# Basic concepts
Botafar allows you to add global low-latency remote controls to your robotics projects.

You can make your robot's remote controls publicly available on [botafar.com](https://botafar.com).
Optionally, you can stream the robot to Twitch or Youtube though OBS compatible video source

TODO

- print
- controls
- community ask

## Function callback

```python
import botafar

b = botafar.Button("A")

@b.on_press
def press():
    print("press")

botafar.run()
```

## Async function callback

```python
import botafar

b = botafar.Button("A")

@b.on_press
async def press():
    print("press")

botafar.run()
```


## Multiple function callbacks

```python
import botafar

b = botafar.Button("A")

@b.on_press
def press():
    print("press 1")

@b.on_press
def press():
    print("press 2")

botafar.run()
```

## Multiple callbacks to same function

```python
import botafar

b1 = botafar.Button("A")
b2 = botafar.Button("SPACE")

@b1.on_press
@b2.on_press
def press():
    print("press 1")

botafar.run()
```

## Class method callback

```python
import botafar

b = botafar.Button("A")

class Bot:
    def __init__(self, name):
        self.name = name

    @b.on_press
    def press(self):
        print(self.name + " pressed")

bot = Bot()
botafar.run()
```

