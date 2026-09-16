# SB24 Text Tools

A small Telegram-native text utility bot built with Python 3.12 and aiogram 3.x.

## Exactly three core functions

1. **Sort Words** — send words and receive them in alphabetical order.
2. **Count Text** — count words, characters, characters without spaces, and lines.
3. **Rearrange Text** — rearrange words or letters into a different order when possible.

All three functions run directly inside Telegram. The bot does not depend on an external website or redirect users elsewhere.

## Commands

- `/start` — opens the main menu and safely handles Telegram start parameters.
- `/help` — explains the three functions.

The main functionality is available through the inline menu.

## Configuration

Required environment variable:

```text
BOT_TOKEN=your_telegram_bot_token_here
```

Never commit a real bot token.

## Run locally

```bash
python -m pip install -r requirements.txt
BOT_TOKEN="YOUR_BOT_TOKEN" python bot.py
```

## Docker

```bash
docker build -t sb24textbot .
docker run --rm -e BOT_TOKEN="YOUR_BOT_TOKEN" sb24textbot
```

## QA

Run:

```bash
python -m pytest -q
```

The test suite covers the three processing functions, limits, dispatcher construction, and the required command/menu content.

## Telegram Ads destination notes

The bot is designed as a genuine Telegram-native utility destination. Its advertised functionality should accurately describe the three available tools. Do not advertise functionality that is not present.
