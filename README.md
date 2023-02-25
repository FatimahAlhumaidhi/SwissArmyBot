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
أوامر البوت:

- `/spell` يتحقق من صحة الإملاء في جملة عربية
- `/randomsong` يرسل لك أغنية عشوائية
- `/define` يرجع لك تعريف كلمة في معجم
- `/whodis` ترسل رقم سعودي ويعطيك الأسماء المسجلة له
- `/animeseason` يرسل لك لستة بأنميات الموسم أسبوعيا
- `/GetLatestChapter` يرسل لك آخر تشابتر نزل لمانجا بترجمة انجليزية

## Extending the Bot

The bot is designed to be easily extensible. To add a new command, create a new function in the `bot.py` file and add a new entry to the `COMMANDS` dictionary. The function should take two arguments: the update and the context.
