# SB24 Text Tools

A Telegram-native utility and updates bot built with Python 3.12 and aiogram 3.x.

## Exactly three user-facing functions

1. **Sort Words** — sort a list of words alphabetically.
2. **Count Text** — count words, characters, characters without spaces, and lines.
3. **News & Updates** — read SB24's own updates directly inside Telegram.

There are no external websites, external news links, or redirect flows in the user experience.

## Commands

- `/start` — opens the main menu and safely accepts Telegram start parameters.
- `/help` — explains the available functions.

## Configuration

Required environment variable:

```text
BOT_TOKEN=your_telegram_bot_token_here
```

Never commit a real token.

## Run

```bash
python -m pip install -r requirements.txt
BOT_TOKEN="YOUR_BOT_TOKEN" python bot.py
```

## Docker

```bash
docker build -t sb24textbot .
docker run --rm -e BOT_TOKEN="YOUR_BOT_TOKEN" sb24textbot
```

## Testing

```bash
python -m pytest -q
```

The bot intentionally has no database because the two processing tools and in-app updates do not require persistent user data.

## Telegram Ads destination

The bot is intended to be a complete Telegram-native destination. Its ad should accurately describe the functions available in the bot. Do not advertise external websites or functionality that does not exist.
