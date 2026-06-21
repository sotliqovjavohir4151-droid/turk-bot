import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
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
                    text="📢 Rasmiy kanal",
                    url="https://t.me/turkustoz"
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Bot haqida",
                    callback_data="about"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👨‍💻 Dasturchi",
                    url="https://t.me/sotiiqov"
                )
            ]
        ]
    )

    await message.answer(
        "🇹🇷 Turk Ustoz botiga xush kelibsiz!\n\n"
        "📚 Turk tilini o‘rganish uchun zamonaviy platforma.\n\n"
        "✅ Darslar\n"
        "✅ Testlar\n"
        "✅ So‘z yodlash mashqlari\n"
        "✅ Interaktiv Mini App\n"
        "✅ Loyihaga kirish uchun chap tomon pastdagi \"Boshlash\" tugmasini bosing\n\n"  # Qo'shtirnoq xatosi tuzatildi
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=keyboard
    )


@dp.callback_query(lambda c: c.data == "about")
async def about(callback: CallbackQuery):
    await callback.message.answer(
        "🇹🇷 TURK USTOZ\n\n"
        "Turk Ustoz — turk tilini o‘rganish uchun yaratilgan "
        "zamonaviy ta'lim platformasi.\n\n"
        "📚 Platforma imkoniyatlari:\n"
        "• A1, A2, B1, B2 darajadagi darslar\n"
        "• Mavzular bo‘yicha testlar\n"
        "• So‘z yodlash mashqlari\n"
        "• Interaktiv Mini App\n"
        "• Grammatik qoidalar\n"
        "• Kundalik turkcha iboralar\n"
        "• O‘quvchilar uchun qulay interfeys\n\n"
        "🎯 Maqsadimiz:\n"
        "Turk tilini o‘rganishni oson, qiziqarli va samarali qilish.\n\n"
        "📱 Mini App imkoniyatlari:\n"
        "• Darslarni o‘qish\n"
        "• Test ishlash\n"
        "• Natijalarni kuzatish\n"
        "• Yangi mavzularni o‘rganish\n"
        "• Bilimingizni mustahkamlash\n\n"
        "🚀 Turk Ustoz bilan turk tilini oson va samarali o‘rganing!"
    )
    await callback.answer()


async def health(request):
    return web.Response(text="Turk Ustoz Bot ishlayapti!")


async def main():
    # Web server sozlamalari
    app = web.Application()
    app.router.add_get("/", health)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print(f"Server {port} portda ishga tushdi")

    # Botni ishga tushirish
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
