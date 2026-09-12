import asyncio
import logging
import os
import random
from html import escape

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set")

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("sb24textbot")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔤 Sort Words"), KeyboardButton(text="🔢 Count Text")],
        [KeyboardButton(text="🔀 Rearrange Letters")],
        [KeyboardButton(text="💡 Examples")],
    ],
    resize_keyboard=True,
    is_persistent=True,
    input_field_placeholder="Choose a text tool...",
)

BACK_MENU = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🏠 Main Menu")]],
    resize_keyboard=True,
    is_persistent=True,
)

user_modes: dict[int, str] = {}

WELCOME = (
    "<b>Welcome to SB24 bot! 📝</b>\n\n"
    "SB24 is a simple text utility bot. Sort words, count text, "
    "or rearrange letters in a few taps.\n\n"
    "Choose a tool below or tap <b>💡 Examples</b> to see how everything works."
)

EXAMPLES = (
    "<b>💡 SB24 Examples</b>\n\n"
    "<b>🔤 Sort Words</b>\n"
    "Send: <code>banana apple orange</code>\n"
    "Result: <code>apple banana orange</code>\n\n"
    "<b>🔢 Count Text</b>\n"
    "Send: <code>Hello world!</code>\n"
    "Result: 2 words, 12 characters, 1 line\n\n"
    "<b>🔀 Rearrange Letters</b>\n"
    "Send: <code>hello</code>\n"
    "Result: a different letter order, when possible.\n\n"
    "Use <b>🏠 Main Menu</b> to return at any time."
)


def count_text(text: str) -> tuple[int, int, int, int]:
    return (
        len(text.split()),
        len(text),
        len("".join(text.split())),
        len(text.splitlines()) if text else 0,
    )


def rearrange_text(text: str) -> str:
    words = text.split()
    if len(words) > 1:
        shuffled = words[:]
        for _ in range(10):
            random.shuffle(shuffled)
            if shuffled != words:
                return " ".join(shuffled)
        return " ".join(shuffled)

    compact = "".join(text.split())
    if len(compact) < 2:
        return compact
    letters = list(compact)
    for _ in range(20):
        random.shuffle(letters)
        result = "".join(letters)
        if result != compact:
            return result
    return "".join(letters)


def clear_mode(user_id: int) -> None:
    user_modes.pop(user_id, None)


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    clear_mode(message.from_user.id)
    await message.answer(WELCOME, reply_markup=MAIN_MENU)


@dp.message(Command("help"))
async def help_handler(message: Message) -> None:
    clear_mode(message.from_user.id)
    await message.answer(
        "<b>SB24 Help</b> 📝\n\n"
        "Choose a text tool from the menu below.\n"
        "Tap <b>💡 Examples</b> to see sample input and output.",
        reply_markup=MAIN_MENU,
    )


@dp.message(F.text == "💡 Examples")
async def examples_handler(message: Message) -> None:
    clear_mode(message.from_user.id)
    await message.answer(EXAMPLES, reply_markup=MAIN_MENU)


@dp.message(F.text == "🏠 Main Menu")
async def menu_handler(message: Message) -> None:
    clear_mode(message.from_user.id)
    await message.answer("<b>Main Menu</b>\nChoose a text tool below:", reply_markup=MAIN_MENU)


@dp.message(F.text == "🔤 Sort Words")
async def sort_words_handler(message: Message) -> None:
    user_modes[message.from_user.id] = "sort"
    await message.answer(
        "<b>🔤 Sort Words</b>\n\n"
        "Send a list of words and I will sort them alphabetically.\n\n"
        "Example: <code>banana apple orange</code>",
        reply_markup=BACK_MENU,
    )


@dp.message(F.text == "🔢 Count Text")
async def count_text_handler(message: Message) -> None:
    user_modes[message.from_user.id] = "count"
    await message.answer(
        "<b>🔢 Count Text</b>\n\n"
        "Send any text and I will count words, characters, characters without spaces, and lines.\n\n"
        "Example: <code>Hello world!</code>",
        reply_markup=BACK_MENU,
    )


@dp.message(F.text == "🔀 Rearrange Letters")
async def rearrange_letters_handler(message: Message) -> None:
    user_modes[message.from_user.id] = "rearrange"
    await message.answer(
        "<b>🔀 Rearrange Letters</b>\n\n"
        "Send letters or words and I will rearrange their order.\n\n"
        "Example: <code>hello world</code>",
        reply_markup=BACK_MENU,
    )


@dp.message(F.text)
async def text_tool_handler(message: Message) -> None:
    user_id = message.from_user.id
    mode = user_modes.get(user_id)
    text = message.text.strip()

    if not mode:
        await message.answer("Please choose one of the text tools below.", reply_markup=MAIN_MENU)
        return

    if mode == "sort":
        words = text.split()
        sorted_words = sorted(words, key=str.casefold)
        result = escape(" ".join(sorted_words))
        await message.answer(
            f"<b>Sorted words</b>\n\n<code>{result}</code>",
            reply_markup=BACK_MENU,
        )
        return

    if mode == "count":
        words, characters, chars_without_spaces, lines = count_text(text)
        await message.answer(
            "<b>Text Count</b>\n\n"
            f"Words: <b>{words}</b>\n"
            f"Characters: <b>{characters}</b>\n"
            f"Characters without spaces: <b>{chars_without_spaces}</b>\n"
            f"Lines: <b>{lines}</b>",
            reply_markup=BACK_MENU,
        )
        return

    if mode == "rearrange":
        result = escape(rearrange_text(text))
        await message.answer(f"<b>Rearranged text</b>\n\n<code>{result}</code>", reply_markup=BACK_MENU)
        return

    clear_mode(user_id)
    await message.answer("Choose a text tool below.", reply_markup=MAIN_MENU)


@dp.message()
async def unsupported_message_handler(message: Message) -> None:
    await message.answer("Please send text or choose a tool from the menu.", reply_markup=MAIN_MENU)


async def main() -> None:
    logger.info("Starting SB24 bot")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
