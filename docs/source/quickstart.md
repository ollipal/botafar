# Quick start

1. Install the library ([help](install.md)):

```
pip install telebotties
```

2. Create and save a **bot.py** file:

```python
import telebotties as tb


b = tb.Button("A")

@b.on_press
def hello():
    tb.print("Hello")

@b.on_release
def world():
    tb.print("World")

tb.run()
```

3. Execute the **bot.py** file with:

```
python bot.py
```

and open the returned link in browser ([help](execute_help.md)).

4. From the browser, add a live video feed by opening the video feed link in a separate tab or another device such as phone.

5. Press the **Try controls** -button. Now when you press and release `A` key from a keyboard or a touch screen, texts "Hello" and "World" get printed on the bottom of the live video feed.

Keep reading if you want to learn how to:

- [Share the bot with others](https://telebotties.com)
- [Make the bot public on telebotties.com](https://telebotties.com)
- [Stream the bot to Twitch or Youtube](https://telebotties.com)

and a lot more!