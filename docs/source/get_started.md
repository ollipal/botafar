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

1. Install the library ([help](https://docs.botafar.com/install))

```
pip install --upgrade botafar
```

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

3. Execute the **main.py** file, and open the returned link in browser. _Note that this browser can be on other device, for example Python program can run on a [Raspberry Pi](https://en.wikipedia.org/wiki/Raspberry_Pi) and the browser setup is done on a desktop PC_ ([help](https://docs.botafar.com/get_started_help)).

```
$ python main.py

Bot running, connect at https://botafar.com/abcde-fghij-klmno
```

4. From the browser, press the **Try controls** -button. Now when you press **A** and **D** keys from a keyboard or a touch screen, texts "hello" and "world" get printed on terminal.

5. Choose a stream source from the browser. It can be a webcam, a phone or a screen share.

6. Give your bot a name and switch it to public

7. **The browser now shows a direct link to your bot you can share with anyone in the world!**

<img src="https://docs-assets.botafar.com/get_started_result.png" border="1px solid red"/>
<!-- ![result](https://docs-assets.botafar.com/get_started_result.png)
 -->

> If you got stuck, have an idea or you found a bug, write about it on the [GitHub discussions forum](https://github.com/ollipal/botafar/discussions). This tool is still under development, and all feedback is appreciated.

**Keep reading if you want to learn how to:**

- Use more botafar features such as [printing text to livestream directly](https://botafar.com)
- Remote control servo motors and LEDs with [Raspberry Pi](https://botafar.com) or [Arduino](https://botafar.com)
- [Forward the livestream to Twitch or Youtube through OBS](https://botafar.com)
