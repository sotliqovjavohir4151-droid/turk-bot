import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Ilovani ochish")],
        [KeyboardButton(text="📢 Rasmiy kanal")],
        [KeyboardButton(text="ℹ️ Bot haqida")],
        [KeyboardButton(text="👨‍💻 Admin bilan bogʻlanish")]
    ],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start(message: Message):
    text = (
        "🇹🇷 Turk Ustoz botiga xush kelibsiz!\n\n"
        "✅ Turk tili darslari\n"
        "✅ Testlar\n"
        "✅ Mini App\n"
        "✅ So‘z yodlash mashqlari\n\n"
        "Kerakli bo‘limni tanlang 👇"
    )

    await message.answer(
        text,
        reply_markup=MENU
    )

@dp.message()
async def buttons(message: Message):

    if message.text == "📱 Ilovani ochish":
        await message.answer(
            "📱 Turk Ustoz Mini App:\n\n"
            "https://turkish-path--sotliqovjavohir.replit.app"
        )

    elif message.text == "📢 Rasmiy kanal":
        await message.answer(
            "📢 Rasmiy kanal:\n\n"
            "https://t.me/turkustoz"
        )

    elif message.text == "ℹ️ Bot haqida":
        await message.answer(
            "🇹🇷 Turk Ustoz\n\n"
            "Turk tilini o‘rganish uchun yaratilgan platforma.\n\n"
            "• Darslar\n"
            "• Testlar\n"
            "• Mini App\n"
            "• So‘zlar bazasi\n"
            "• Interaktiv mashqlar"
        )

    elif message.text == "👨‍💻 Admin bilan bogʻlanish":
        await message.answer(
            "👨‍💻 Admin:\n"
            "@sotiiqov"
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

    print(f"Server {port} portda ishga tushdi")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
