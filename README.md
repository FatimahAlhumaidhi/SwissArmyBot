# Python Telegram Bot

This is a Python Telegram Bot built using the `python-telegram-bot` library. The bot is designed to perform various tasks and respond to user input on the Telegram messaging platform.

## Requirements

Install bot dependencies by running the following command:

```
pip install -r requirements.txt
```

## Configuration

Before running the bot, you will need to obtain a Telegram Bot Token. You can create a new bot and obtain a token by following the instructions on the Telegram documentation: https://core.telegram.org/bots#3-how-do-i-create-a-bot

create a new file `.env` and add your bot token and any other necessary keys

run the bot, simply run the `bot.py` file using Python:

```
python bot.py
```

The bot will then start and listen for incoming messages on your Telegram Bot.

## Features

The bot currently supports the following commands:

/define this command searches for the specified word in almaany.com and returns part of the resulted output.* 

/whodis this command uses an API to look up names registered for a saudi number (formatted 05XXXXXXXX).*

/animeseason this command uses jikan.moe (UNOFFICIAL MYANIMELIST API) to get the latest anime news for this season. 

/getlatestchapter this command uses mangadex.org API to get the latest chapter for a specified manga.*

/spell this command uses the King Saud University Corpus of Classical Arabic (KSUCCA) as a refrence to fix arabic words in a message using string matching (the corpus contains 377366 unique words).

/randomsong this command uses spotify API to request a song based on a randmonly chosen genre.

*commands specified with an astrik needs context in the same command message (e.g. /define بقسماط).

contact https://t.me/westandasone for suggestions or questions.

## Extending the Bot

The bot is designed to be easily extensible. To add a new command, create a new function in the `bot.py` file and add a new entry to the `COMMANDS` dictionary. The function should take two arguments: the update and the context.
