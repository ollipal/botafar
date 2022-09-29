# Twitch & YouTube

## Why to stream to Twitch/YouTube

Botafar makes streaming you bot to [Twitch](https://www.twitch.tv/) or [YouTube](https://www.youtube.com/) simple by integrating with [OBS](https://obsproject.com/) and [Streamlabs Desktop](https://streamlabs.com/) through their built-in browser source.

Without external livestreaming, only the owner and currently remote controlling player can see the low-latency livestream and related print messages on screen. Botafar also does not support many social features such as chatting between players and between player and the owner, so this should be done through these platforms.

This tutorial goes through how to livestream your bot with OBS to Twitch or YouTube, but as Streamlabs Desktop [is based on a fork of OBS](https://en.wikipedia.org/wiki/Streamlabs), the steps are identical to connecting with OBS. Read about Streamlabs Desktop browser source [here](https://blog.streamlabs.com/introducing-browser-source-interaction-for-streamlabs-obs-d8fc4dcbb1fb).

>As seen [later on this page](https://docs.botafar.com/twitch_and_youtube.html#streaming-to-youtube), YouTube **requires you to wait 24 hours before your first livestream** after you have clicked "Go live" button for the first time. So if you even consider livestreaming your bot at some point on YouTube, I suggest you go click "Go live" just in case as soon as possible.

## Connecting to OBS

Before you start, [download](https://obsproject.com/download) and install OBS. It has Windows, Mac and Linux support. On the botafar website, select a stream source if you have not already done so.

1. Click show more options

![show_more.png](https://docs-assets.botafar.com/show_more.png)

2. Click "Copy OBS link"

![copy_obs_link.png](https://docs-assets.botafar.com/copy_obs_link.png)

3. On Obs, from sources, click "add", and then select "browser"

![add_source.png](https://docs-assets.botafar.com/add_source.png)

4. The default name "Browser" is ok, but you can change it to for example "botafar" if you want. Click ok.

![create_new.png](https://docs-assets.botafar.com/create_new.png)

5. Right click "URL" and **paste the OBS link you copied earlier**. Set "Width" to **1920** and "Height" to **1080**. Then click ok.

![browser_properties](https://docs-assets.botafar.com/browser_properties.png)

6. You should see text "connecting..." briefly and the your livestream from the bot!

![obs_success](https://docs-assets.botafar.com/obs_success.png)

**You are now ready to move to [Streaming to Twitch](https://docs.botafar.com/twitch_and_youtube.html#twitch-streaming) or [Streaming to YouTube](https://docs.botafar.com/twitch_and_youtube.html#youtube-streaming) below.**

>In some rare cases, the livestream does not connect immediately. In that case, click "reset stream" from the browser and select stream source again. Then from OBS, activate the browser source by clicking it, and then click "Refresh".

![reset_stream](https://docs-assets.botafar.com/reset_stream.png)

![refresh_interact](https://docs-assets.botafar.com/refresh_interact.png)

## Twitch streaming

The next step is to connect OBS to Twitch and start the livestream. Chris' Tutorials YouTube channel has a really nice video [OBS Stream to Twitch 5 Minute Setup Guide 2022](https://www.youtube.com/watch?v=9HYB9N7_cZc) which goes through this process.

_If you are familiar with Twitch livestreaming and want to give tips on setting up a remote controlling/robotics related livestream, write to [Github Discussions](https://github.com/ollipal/botafar/discussions/categories/general)!_
## YouTube streaming

The next step is to connect OBS to YouTube and start the livestream.

Before you can start livestreaming on YouTube, you must go to the top right corner of the web page, click the camera icon and then click "Go live".

![go_live](https://docs-assets.botafar.com/go_live.png)

This will forward you to another page, which after a refresh will show "Only 24 hours until you can stream"

**So you must wait this 24 hours before you can start livestreaming** for the first time.

Chris' Tutorials YouTube channel has a really nice video [6 Minutes to Setup YouTube Streaming from OBS Tutorial 2022](https://www.youtube.com/watch?v=e3-ccdPmYuM) which goes through the process of starting a YouTube livestream after you have waited 24 hours.

Another good video I recommend to watch is Senpai Gaming's [Live Streaming On YouTube -- EVERYTHING You Need To Know](https://www.youtube.com/watch?v=qXzUOOD7Or0).

_If you are familiar with YouTube livestreaming and want to give tips on setting up a remote controlling / robotics related livestream, write to [Github Discussions](https://github.com/ollipal/botafar/discussions/categories/general)!_