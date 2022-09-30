# Get started

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

## botafar setup

1. Install the library ([help](install))

```
pip install --upgrade botafar
```

On some Debian based operating systems such as Raspberry Pi OS, on you need to have [libSRTP](https://github.com/cisco/libsrtp) and the other related network dependencies installed to be installed as well: `sudo apt install libnss3 libnspr4 libsrtp2-1 -y`

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

3. Execute the **main.py** file, and open the returned link in browser. _Note that this browser can be on other device, for example Python program can run on a [Raspberry Pi](https://en.wikipedia.org/wiki/Raspberry_Pi) and the browser setup is done on a desktop PC_ ([help](get_started_help)).

```
$ python main.py

Bot running, connect at https://botafar.com/abcde-fghij-klmno
```

4. From the browser, press the **Try controls** -button. Now when you press <kbd>A</kbd> and <kbd>D</kbd> keys from a keyboard or a touch screen, texts "hello" and "world" get printed on terminal.

5. Choose a stream source from the browser. It can be a webcam, a phone or a screen share.

6. Give your bot a name and switch it to public

7. **The browser now shows a direct link to your bot you can share with anyone in the world!**

<img src="https://docs-assets.botafar.com/get_started_result.png"/>

> If you got stuck, have an idea or you found a bug, write about it on the [GitHub discussions forum](https://github.com/ollipal/botafar/discussions). This tool is still under development, and all feedback is appreciated.

**Keep reading if you want to learn how to:**

- Use more botafar features such as [printing text to livestream directly](https://docs.botafar.com/basics.html#print)
- Remote control servo motors and LEDs with [Arduino](arduino) or [Raspberry Pi](raspi)
- [Forward the livestream to Twitch or Youtube through OBS](twitch_and_youtube)
