# botafar [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<!-- start intro -->

Add **global remote controls** and **a real time livestream** to your project

- Share a link and let others take the controls one by one
- Forward the livestream to Twitch or YouTube (optional)
- No hardware required, a phone can be used as a camera
- [Arduino](https://docs.botafar.com/arduino) and [Raspberry Pi](https://docs.botafar.com/raspi) tutorials available
- Desktop and mobile browser support, no apps, no signups
- 100% free to use, open-source Python library

It works by decorating existing functions and class methods to respond to user input:

```python
import botafar

steering = botafar.Joystick("W","A","S","D")

@steering.on_left
def turn_left():
    print("left!")

@steering.on_right
def turn_right():
    print("right!")

# ...@on_up, on_down, on_center

botafar.run() 
```

![result](https://docs-assets.botafar.com/readme.png)

<!-- end intro -->

**[GET STARTED](https://docs.botafar.com/get_started)**
