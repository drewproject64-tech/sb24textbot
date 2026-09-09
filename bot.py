import logging
import os
import random
from itertools import islice

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("sb24textbot")

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()

MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔤 Sort Words")],
        [KeyboardButton(text="🔢 Count Text")],
        [KeyboardButton(text="🔀 Rearrange Letters")],
    ],
    resize_keyboard=True,
    is_persistent=True,
)

BACK_MENU = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🏠 Main Menu")]],
    resize_keyboard=True,
)

# Tracks the utility the user is currently using.
user_modes: dict[int, str] = {}

WELCOME = (
    "<b>Welcome to SB24 bot!</b> 📝\n\n"
    "A simple text utility bot for sorting words, counting text, "
    "and rearranging letters.\n\n"
    "Choose a tool below to get started."
)


def count_text(text: str) -> tuple[int, int, int, int]:
    words = len(text.split())
    characters = len(text)
    characters_no_spaces = len("".join(text.split()))
    lines = len(text.splitlines()) if text else 0
    return words, characters, characters_no_spaces, lines


def rearrange_text(text: str) -> str:
    # Preserve the user's words while producing a new ordering where possible.
    words = text.split()
    if len(words) > 1:
        shuffled = words[:]
        for _ in range(5):
            random.shuffle(shuffled)
            if shuffled != words:
                return " ".join(shuffled)
        return " ".join(shuffled)

    letters = list(text.replace(" ", ""))
    if len(letters) < 2:
        return text

    original = "".join(letters)
    for _ in range(10):
        random.shuffle(letters)
        result = "".join(letters)
        if result != original:
            return result
    return "".join(letters)


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    user_modes.pop(message.from_user.id, None)
    await message.answer(WELCOME, reply_markup=MENU)


@dp.message(F.text == "🏠 Main Menu")
async def menu_handler(message: Message) -> None:
    user_modes.pop(message.from_user.id, None)
    await message.answer("Choose a text tool:", reply_markup=MENU)


@dp.message(F.text == "🔤 Sort Words")
async def sort_words_handler(message: Message) -> None:
    user_modes[message.from_user.id] = "sort"
    await message.answer(
        "Send the words you want to sort alphabetically.\n\n"
        "Example: <code>banana apple orange</code>",
        reply_markup=BACK_MENU,
    )


@dp.message(F.text == "🔢 Count Text")
async def count_text_handler(message: Message) -> None:
    user_modes[message.from_user.id] = "count"
    await message.answer(
        "Send any text and I will count the words, characters, and lines.",
        reply_markup=BACK_MENU,
    )


@dp.message(F.text == "🔀 Rearrange Letters")
async def rearrange_letters_handler(message: Message) -> None:
    user_modes[message.from_user.id] = "rearrange"
    await message.answer(
        "Send letters or words and I will rearrange them into a new order.\n\n"
        "Example: <code>hello world</code>",
        reply_markup=BACK_MENU,
    )


@dp.message(F.text)
async def text_tool_handler(message: Message) -> None:
    user_id = message.from_user.id
    mode = user_modes.get(user_id)
    text = message.text.strip()

    if mode == "sort":
        words = text.split()
        if not words:
            await message.answer("Please send at least one word.", reply_markup=BACK_MENU)
            return
        sorted_words = sorted(words, key=str.casefold)
        await message.answer(
            "<b>Sorted words:</b>\n<code>" + " ".join(sorted_words) + "</code>",
            reply_markup=BACK_MENU,
        )
        return

    if mode == "count":
        words, characters, chars_no_spaces, lines = count_text(text)
        await message.answer(
            "<b>Text count</b>\n\n"
            f"Words: <b>{words}</b>\n"
            f"Characters: <b>{characters}</b>\n"
            f"Characters without spaces: <b>{chars_no_spaces}</b>\n"
            f"Lines: <b>{lines}</b>",
            reply_markup=BACK_MENU,
        )
        return

    if mode == "rearrange":
        if not text:
            await message.answer("Please send some letters or words.", reply_markup=BACK_MENU)
            return
        result = rearrange_text(text)
        await message.answer(
            "<b>Rearranged:</b>\n<code>" + result + "</code>",
            reply_markup=BACK_MENU,
        )
        return

    await message.answer("Choose one of the 3 tools below.", reply_markup=MENU)


async def main() -> None:
    logger.info("Starting SB24 bot")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
