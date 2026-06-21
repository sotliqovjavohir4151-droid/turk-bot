import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📱 Ilovani ochish",
                    url="https://turkish-path--sotliqovjavohir.replit.app"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 Rasmiy kanal",
                    url="https://t.me/turkustoz"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👨‍💻 Admin bilan bogʻlanish",
                    url="https://t.me/sotiiqov"
                )
            ]
        ]
    )

    await message.answer(
        "🇹🇷 Turk Ustoz botiga xush kelibsiz!\n\n"
        "Turk tilini o‘rganish uchun darslar, testlar va mashqlar platformasi.",
        reply_markup=keyboard
    )


async def health(request):
    return web.Response(text="Turk Ustoz Bot ishlayapti!")


async def main():
    app = web.Application()
    app.router.add_get("/", health)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
