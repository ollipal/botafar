# Quick start

1. Install the Python library ([more detailed install instructions](http://telebotties.com)):

```
pip install telebotties
```

2. Create a **main.py** file:

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

3. Execute the **main.py** file with `python main.py` or `python3 main.py` command, and open the returned link in browser.

4. From the browser, select a video source (a phone camera for an example)

5. Press the **Control Bot** -button. Now when you press and release `A` key from a keyboard, texts "Hello" and "World" get printed on screen.

Next you can [share the bot link to others](https://telebotties.com), [make the bot public](https://telebotties.com) or [stream the bot](https://telebotties.com) to Twitch or Youtube!
