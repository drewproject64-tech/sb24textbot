from __future__ import annotations

import asyncio
import logging
import os
import random
from html import escape

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BotCommand, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("sb24textbot")

MAX_TEXT_LENGTH = 4000


class ToolState(StatesGroup):
    waiting_for_input = State()


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔤 Sort Words", callback_data="tool:sort"),
                InlineKeyboardButton(text="🔢 Count Text", callback_data="tool:count"),
            ],
            [InlineKeyboardButton(text="🔀 Rearrange Text", callback_data="tool:rearrange")],
            [InlineKeyboardButton(text="ℹ️ Help", callback_data="help")],
        ]
    )


def back_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔁 Run Again", callback_data="retry")],
            [InlineKeyboardButton(text="🏠 Main Menu", callback_data="home")],
        ]
    )


def input_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Main Menu", callback_data="home")],
        ]
    )


WELCOME = (
    "<b>Welcome to SB24 Text Tools 📝</b>\n\n"
    "A simple Telegram-native text utility bot. Process your text directly in this chat "
    "with three tools:\n\n"
    "🔤 <b>Sort Words</b> — sort words alphabetically.\n"
    "🔢 <b>Count Text</b> — count words, characters and lines.\n"
    "🔀 <b>Rearrange Text</b> — rearrange words or letters.\n\n"
    "Choose a tool below to get started."
)

HELP_TEXT = (
    "<b>SB24 Help</b> ℹ️\n\n"
    "<b>🔤 Sort Words</b>\n"
    "Send a list of words. SB24 returns them in alphabetical order.\n\n"
    "<b>🔢 Count Text</b>\n"
    "Send any text. SB24 counts words, characters, characters without spaces, and lines.\n\n"
    "<b>🔀 Rearrange Text</b>\n"
    "Send words or letters. SB24 returns a different order when possible.\n\n"
    "Text input is limited to 4,000 characters. All processing happens inside Telegram.\n\n"
    "Use <b>/start</b> at any time to return to the main menu."
)


def count_text(text: str) -> tuple[int, int, int, int]:
    return (
        len(text.split()),
        len(text),
        len("".join(text.split())),
        len(text.splitlines()) if text else 0,
    )


def sort_words(text: str) -> str:
    words = text.split()
    return " ".join(sorted(words, key=str.casefold))


def rearrange_text(text: str) -> str:
    words = text.split()
    if len(words) > 1:
        original = words[:]
        shuffled = words[:]
        for _ in range(20):
            random.shuffle(shuffled)
            if shuffled != original:
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


def tool_prompt(tool: str) -> str:
    prompts = {
        "sort": (
            "<b>🔤 Sort Words</b>\n\n"
            "Send a list of words and I will sort them alphabetically.\n\n"
            "Example: <code>banana apple orange</code>"
        ),
        "count": (
            "<b>🔢 Count Text</b>\n\n"
            "Send any text and I will count words, characters, characters without spaces, and lines.\n\n"
            "Example: <code>Hello world!</code>"
        ),
        "rearrange": (
            "<b>🔀 Rearrange Text</b>\n\n"
            "Send words or letters and I will rearrange their order when possible.\n\n"
            "Example: <code>hello world</code>"
        ),
    }
    return prompts[tool]


def tool_label(tool: str) -> str:
    return {
        "sort": "🔤 Sort Words",
        "count": "🔢 Count Text",
        "rearrange": "🔀 Rearrange Text",
    }[tool]


async def show_home(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(WELCOME, reply_markup=main_menu())


async def show_help(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(HELP_TEXT, reply_markup=main_menu())


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start_handler(message: Message, state: FSMContext) -> None:
        await show_home(message, state)

    @dp.message(Command("help"))
    async def help_handler(message: Message, state: FSMContext) -> None:
        await show_help(message, state)

    @dp.callback_query(F.data == "home")
    async def home_callback(callback: CallbackQuery, state: FSMContext) -> None:
        await callback.answer()
        await state.clear()
        await callback.message.edit_text(WELCOME, reply_markup=main_menu())

    @dp.callback_query(F.data == "help")
    async def help_callback(callback: CallbackQuery, state: FSMContext) -> None:
        await callback.answer()
        await state.clear()
        await callback.message.edit_text(HELP_TEXT, reply_markup=main_menu())

    @dp.callback_query(F.data.startswith("tool:"))
    async def tool_callback(callback: CallbackQuery, state: FSMContext) -> None:
        tool = (callback.data or "").split(":", 1)[1]
        if tool not in {"sort", "count", "rearrange"}:
            await callback.answer("That tool is not available.", show_alert=True)
            return

        await callback.answer()
        await state.set_state(ToolState.waiting_for_input)
        await state.update_data(tool=tool)
        await callback.message.edit_text(tool_prompt(tool), reply_markup=input_menu())

    @dp.callback_query(F.data == "retry")
    async def retry_callback(callback: CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()
        tool = data.get("tool")
        if tool not in {"sort", "count", "rearrange"}:
            await callback.answer("Please choose a tool first.", show_alert=True)
            await state.clear()
            await callback.message.edit_text(WELCOME, reply_markup=main_menu())
            return

        await callback.answer()
        await state.set_state(ToolState.waiting_for_input)
        await callback.message.edit_text(tool_prompt(tool), reply_markup=input_menu())

    @dp.message(ToolState.waiting_for_input, F.text)
    async def process_text(message: Message, state: FSMContext) -> None:
        text = (message.text or "").strip()
        data = await state.get_data()
        tool = data.get("tool")

        if tool not in {"sort", "count", "rearrange"}:
            await state.clear()
            await message.answer(
                "Your session expired. Please choose a tool from the main menu.",
                reply_markup=main_menu(),
            )
            return

        if not text:
            await message.answer(
                "That input is empty. Please send some text and try again.",
                reply_markup=input_menu(),
            )
            return

        if len(text) > MAX_TEXT_LENGTH:
            await message.answer(
                f"That text is too long. Please keep it to {MAX_TEXT_LENGTH:,} characters or fewer.",
                reply_markup=input_menu(),
            )
            return

        try:
            if tool == "sort":
                result = sort_words(text)
                response = f"<b>🔤 Sorted Words</b>\n\n<code>{escape(result)}</code>"
            elif tool == "count":
                words, characters, without_spaces, lines = count_text(text)
                response = (
                    "<b>🔢 Text Count</b>\n\n"
                    f"Words: <b>{words}</b>\n"
                    f"Characters: <b>{characters}</b>\n"
                    f"Characters without spaces: <b>{without_spaces}</b>\n"
                    f"Lines: <b>{lines}</b>"
                )
            else:
                result = rearrange_text(text)
                response = f"<b>🔀 Rearranged Text</b>\n\n<code>{escape(result)}</code>"

            await state.update_data(tool=tool)
            await message.answer(response, reply_markup=back_menu())
        except Exception:
            logger.exception("Text processing failed for tool=%s", tool)
            await message.answer(
                "I couldn't process that text. Please try again.",
                reply_markup=back_menu(),
            )

    @dp.message(ToolState.waiting_for_input)
    async def unsupported_tool_input(message: Message) -> None:
        await message.answer(
            "Please send text for this tool, or use Main Menu to choose another option.",
            reply_markup=input_menu(),
        )

    @dp.message()
    async def fallback(message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer(
            "Please use /start or choose one of the three tools below.",
            reply_markup=main_menu(),
        )

    return dp


async def main() -> None:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable is not set")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = build_dispatcher()

    logger.info("Starting SB24 Text Tools")
    try:
        await bot.set_my_commands(
            [
                BotCommand(command="start", description="Open the text tools menu"),
                BotCommand(command="help", description="Learn how the three tools work"),
            ]
        )
        await bot.set_my_short_description("Three simple text tools that work directly in Telegram.")
        await bot.set_my_description(
            "SB24 Text Tools lets you sort words, count text, and rearrange text directly inside Telegram."
        )
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Bot configuration completed; starting polling")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except TelegramAPIError:
        logger.exception("Telegram API error while starting or running the bot")
        raise
    finally:
        await bot.session.close()
        logger.info("SB24 Text Tools stopped")


if __name__ == "__main__":
    asyncio.run(main())
