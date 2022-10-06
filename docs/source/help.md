---
orphan: true
---

# Help

Help with [Get started guide](get_started.md), [Arduino](arduino) and [Raspberry Pi](raspi) tutorials:

## Executing Python file

On most operating systems, executing a file called **main.py** can be done with a command:

```
python main.py
```

but it can also be:

```
python3 main.py
```

or

```
py main.py
```

If none of these work, check the [detailed installation instructions](install.md) for more help.

## Supported browsers

- Make sure to use the latest versions of Chrome, Safari, Firefox or Edge as browser, or anything that is based on Chromium. Some users have reported that Firefox does not work as well as Chrome, so if you face issues with Firefox, try Chrome instead.

## Mobile devices

- On mobile devices, make sure you have the latest system update installed, especially with iPhones.
- If you plan on streaming from a camera for a long time, consider dimming the screen so it does not drain battery or overheat.

## Raspberry Pi browser and video

- Raspberry Pis: most likely you want to open the browser link from Python **with some other device, such as a desktop PC or a phone**. But the Raspberry Pi's browser can still work with some more powerful Raspberry Pi models, such as 3b and 4, and it is the only option if you want to use Raspberry Pi Camera Module. Then [enabling hardware acceleration](https://www.linuxuprising.com/2021/04/how-to-enable-hardware-acceleration-in.html) might increase the performance.
- If you need graphical remote control, where a SSH connection is not enough, and HDMI is not an option, [VNC](https://github.com/gitbls/RPiVNCHowTo) can be used.
- If you have Raspberry Pi OS Lite and need a browser, it seems that [headless browser with Puppeteer](https://www.youtube.com/watch?v=6LnJ1zW5464) is a thing on Raspberry Pi, but this has not yet been attempted with botafar.
