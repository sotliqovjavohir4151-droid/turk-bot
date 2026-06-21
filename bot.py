import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    WebAppInfo,
    FSInputFile
)
from aiogram import F

# =============== BOT TOKEN ===============
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# =============== ADMIN USER ID ===============
ADMIN_USER_ID = 8735290324  # SIZNING ID INGIZ

# =============== /start HANDLER ===============
@dp.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    
    # Rasmni yuklash
    photo = FSInputFile("welcome.jpg")
    
    # Tugmalar - hammaga ko'rinadigan
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Ilovani ochish",
                    web_app=WebAppInfo(url="https://turkish-path--sotliqovjavohir.replit.app")
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
    
    # Rasm va caption yuborish
    await message.answer_photo(
        photo=photo,
        caption=(
            "🇹🇷 Turk Ustoz botiga xush kelibsiz!\n\n"
            "📚 Turk tilini o‘rganish uchun zamonaviy platforma.\n\n"
            "✅ Darslar\n"
            "✅ Testlar\n"
            "✅ So‘z yodlash mashqlari\n"
            "✅ Interaktiv Mini App\n"
            "✅ Natijalar statistikasi\n\n"
            "Kerakli bo‘limni tanlang 👇"
        ),
        reply_markup=keyboard
    )

# =============== ABOUT CALLBACK HANDLER ===============
@dp.callback_query(F.data == "about")
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

# =============== MAXSUS SO'Z UCHUN HANDLER (FAQAT ADMIN UCHUN) ===============
@dp.message()
async def handle_special_word(message: Message):
    """Handle specific word '1Javohir2005' - faqat admin uchun statistika"""
    user_id = message.from_user.id
    text = message.text.lower() if message.text else ""
    
    # Check for the special word - faqat admin uchun
    if "1javohir2005" in text or "1javohir" in text:
        # Faqat admin ko'ra oladi
        if user_id == ADMIN_USER_ID:
            # Bu yerda sizning statistika kodingiz
            await message.reply(
                "📊 **BARCHA FOYDALANUVCHILAR STATISTIKASI**\n\n"
                "👥 Jami foydalanuvchilar: 150\n"
                "📈 Bugun qo'shilganlar: 5\n"
                "💬 Faol foydalanuvchilar: 42\n\n"
                "📊 Eng faol foydalanuvchilar:\n"
                "1. @user1 - 45 ta amal\n"
                "2. @user2 - 38 ta amal\n"
                "3. @user3 - 32 ta amal\n\n"
                "📅 Oxirgi 7 kun: +28 foydalanuvchi"
            )
        else:
            # Boshqa foydalanuvchilar uchun maxfiy
            await message.reply(
                "🔒 Bu maxfiy ma'lumot!\n"
                "Faqat administrator ko'ra oladi."
            )
        return
    
    # Handle other messages
    await message.answer(
        "❓ Iltimos, /start buyrug'ini bosing yoki tugmalardan foydalaning."
    )
