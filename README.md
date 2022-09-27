# Botafar [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<!-- start intro -->

**Create and share robots with real-time remote controls**

**Stream to Twitch or YouTube and let viewers control your robot one by one**

- No hardware required to get started
- [Arduino](https://docs.botafar.com/arduino) and [Raspberry Pi](https://docs.botafar.com/raspi) tutorials available
- OBS and Streamlabs compatible video source
- Simple open-source Python library

Check [botafar.com](https://botafar.com) for currently online bots!

<!-- end intro -->

## Quick start

<!-- start quickstart -->

1. Install the library ([help](https://docs.botafar.com/install)):

```
pip install --upgrade botafar
```

2. Create and save a **bot.py** file:

```python
import botafar as tb


b = tb.Button("A")

@b.on_press
def hello():
    tb.print("Hello")

@b.on_release
def world():
    tb.print("World")

tb.run()
```

3. Execute the **bot.py** file with

```
python bot.py
```

and open the returned link in browser ([help](https://docs.botafar.com/quickstart_help)).

4. From the browser, add a live video feed by opening the video feed link in a separate tab or another device such as phone.

5. Press the **Try controls** -button. Now when you press and release `A` key from a keyboard or a touch screen, texts "Hello" and "World" get printed on the bottom of the live video feed.

<!-- end quickstart -->

Check [the full documentation](https://docs.botafar.com/quickstart) if you want to learn how to:

- [Share the bot with others](https://botafar.com)
- [Make the bot public on botafar.com](https://botafar.com)
- [Stream the bot to Twitch or Youtube](https://botafar.com)

and a lot more!