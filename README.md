# Youtube channel bot
Telegram bot to search youtube channels using filters. You can find the bot at http://t.me/youtube_channel2_bot
The bot uses the YouTube data API to find channels and the htmlcsstoimage API to convert html to image to make results more beautiful.

## Using the bot
- Go to http://t.me/youtube_channel2_bot and start a chat with the bot

*There are several supported commands:*
- **/show_filters** shows your current filters
- **/edit_filters** gives you an opportunity to change your filters
- **/search** searching youtube channels using your filters

*You can filter by:*
1) the number of subscribers
2) the number of videos
3) the number of views
4) the average views by video 

## Creating your bot
### Prerequisites

Python 3.10.x installed

### Installation

```
git clone https://github.com/mikhailsinyakov/youtube_channel_bot.git
cd youtube_channel_bot
python3 -m pip install -r requirements.txt
```

- Create a new bot in BotFather using /newbot command
- Get API token
- Get Google API key following steps at https://developers.google.com/youtube/v3/getting-started
- Get user id and api key at https://htmlcsstoimage.com/
- Create an .env file and save your tokens in it
```
BOT_API_TOKEN = {YOUR_API_TOKEN}
GOOGLE_API_KEY = {YOUR_GOOGLE_API_TOKEN}
HTMLCSS_TO_IMAGE_USER_ID = {YOUR_USER_ID}
HTMLCSS_TO_IMAGE_API_KEY = {YOUR_API_KEY}
```

### Run it

```
python3 bot.py
```
