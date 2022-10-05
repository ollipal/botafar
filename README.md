# botafar [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<!-- start intro -->

Add **global remote controls** and **a real time livestream** to your project

- Share a link and let others take the controls one by one
- Forward the livestream to Twitch or YouTube (optional)
- No hardware required, a phone can be used as a camera
- [Arduino](https://docs.botafar.com/arduino) and [Raspberry Pi](https://docs.botafar.com/raspi) tutorials available
- Desktop and mobile browser support, no apps, no signups

It works by decorating existing functions and class methods to respond to user input:

```python
import botafar

j = botafar.Joystick("W","A","S","D")

@j.on_left
def turn_left():
    print("left!")

@j.on_right
def turn_right():
    print("right!")

# ...@j.on_up, on_down, on_center

botafar.run()
```

![result](https://docs-assets.botafar.com/readme.png)

Check [botafar.com](https://botafar.com/) for currently online bots!

<!-- end intro -->

## Get started

<!-- start get_started -->

### Starting scenario

Let's suppose you have a [Python](https://en.wikipedia.org/wiki/Python_(programming_language)) project, **main.py**, which has two functions `greet` and `target`:

```python
def greet():
    print("hello")

def target():
    print("world")

greet()
target()
```

You want be able to share a link through which people can **remotely call these functions on your hardware**, and **see the results in real life through a low-latency livestream** (and optionally, on Twitch or YouTube as well).

_botafar_ enables you to do all these things.

### Add remote controls and livestreaming

1. Install the library ([help](https://docs.botafar.com/install))

```
pip install --upgrade botafar
```

> On some Debian based operating systems such as Raspberry Pi OS, on you need to have [libSRTP](https://github.com/cisco/libsrtp) and other related network dependencies installed to be installed as well: `sudo apt install libnss3 libnspr4 libsrtp2-1 -y`

2. Modify **main.py**:

- Import botafar
- Create a control, `Joystick` in this example, and bind 4 keys from keyboard to it
- Use decorators (@-symbol) to select functions to call on user input
- Call `botafar.run()`

```python
import botafar

j = botafar.Joystick("W","A","S","D")

@j.on_left
def greet():
    print("hello")

@j.on_right
def target():
    print("world")

botafar.run()
```

3. Execute the **main.py** file, and open the returned link in browser. _Note that this browser can be on other device, for example the Python program can run on a [Raspberry Pi](https://en.wikipedia.org/wiki/Raspberry_Pi) and the browser setup is done on a desktop PC's browser_ ([help](https://docs.botafar.com/get_started_help)).

```
$ python main.py

Bot running, connect at https://botafar.com/abcde-fghij-klmno
```

4. From the browser, press the **Try controls** -button. Now when you press <kbd>A</kbd> and <kbd>D</kbd> keys from a keyboard or a touch screen, texts "hello" and "world" get printed on terminal.

```
$ python main.py

Bot running, connect at https://botafar.com/abcde-fghij-klmno
hello
world
hello
world
```

5. Choose a stream source from the browser. It can be a webcam, a phone or a screen share.

6. Give your bot a name and switch it to public

7. **The browser now shows a direct link to your bot you can share with anyone in the world!** Others can press keyboard or touch screen to print "hello" and "world" to the terminal, and see the prints through a low-latency livestream.

<img src="https://docs-assets.botafar.com/get_started_result.png"/>

> If you got stuck, have an idea or you found a bug, write about it on the [GitHub discussions forum](https://github.com/ollipal/botafar/discussions). This tool is still under development, and all feedback is appreciated.

**Keep reading if you want to learn how to:**

- Use more botafar features such as [printing text to livestream directly](https://docs.botafar.com/basics.html#print)
- Remote control servos and LEDs with [Arduino](https://docs.botafar.com/arduino) or [Raspberry Pi](https://docs.botafar.com/raspi)
- [Forward the livestream to Twitch or Youtube through OBS](https://docs.botafar.com/twitch_and_youtube)

<!-- end get_started -->