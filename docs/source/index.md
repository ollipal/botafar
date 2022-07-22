# Telebotties

Telebotties allows you to add a global low-latency remote control to your robotics projects.

You can share your bot with the world by making it public on [telebotties.com](https://telebotties.com) and you can optionally stream it to Twitch or YouTube through an OBS compatible video source.

No hardware is required to get started, [Arduino](https://telebotties.com) and [Raspberry Pi](https://telebotties.com) tutorials available!

## Quick start:

Install the Python library:

```
pip install telebotties
```

Create a **main.py** file:

```python
import telebotties as tb


button = tb.Button("A")

@button.on_press
def hello():
    tb.print("Hello")

@button.on_release
def world():
    tb.print("World")

tb.run()
```

Execute the file with `python main.py` or `python3 main.py`, and then open the printed link in browser.

From the browser you can select a video source (a phone camera for an example), and control the bot by pressing "Control bot". When you press and release `A` key from keyboard, texts "Hello" and "World" get printed on screen.

Next you can [share the bot link to others](https://telebotties.com), [make the bot public](https://telebotties.com) or [stream the bot](https://telebotties.com) to Twitch or Youtube!
