import os
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    WebAppInfo,
    FSInputFile,
    BufferedInputFile
)
from aiogram import F
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramNetworkError
import aiohttp
import asyncio

# =============== LOGGING ===============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# =============== BOT TOKEN ===============
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.error("❌ BOT_TOKEN topilmadi!")
    sys.exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# =============== ADMIN USER ID ===============
ADMIN_USER_ID = 8735290324

# =============== ASOSIY MENYU FUNKSIYASI ===============
def get_main_keyboard():
    """Asosiy menyu tugmalari"""
    return InlineKeyboardMarkup(
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

def get_main_caption():
    """Asosiy menyu caption matni"""
    return (
        "🇹🇷 Turk Ustoz botiga xush kelibsiz!\n\n"
        "📚 Turk tilini o'rganish uchun zamonaviy platforma.\n\n"
        "✅ Darslar\n"
        "✅ Testlar\n"
        "✅ So'z yodlash mashqlari\n"
        "✅ Interaktiv Mini App\n"
        "✅ Natijalar statistikasi\n\n"
        "Kerakli bo'limni tanlang 👇"
    )

# =============== RASMNI TEKSHIRISH FUNKSIYASI ===============
def get_banner_photo():
    """Rasm faylini tekshirib, mavjud bo'lsa qaytaradi"""
    try:
        if os.path.exists("welcome.jpg"):
            file_size = os.path.getsize("welcome.jpg")
            logger.info(f"Rasm topildi. Hajmi: {file_size} bayt")
            
            if file_size > 20 * 1024 * 1024:
                logger.warning("Rasm hajmi 20MB dan katta!")
                return None
            
            return FSInputFile("welcome.jpg")
        else:
            logger.warning("Rasm fayli topilmadi: welcome.jpg")
            return None
    except Exception as e:
        logger.error(f"Rasmni tekshirishda xatolik: {e}")
        return None

# =============== /start HANDLER ===============
@dp.message(CommandStart())
async def start(message: Message):
    try:
        user_id = message.from_user.id
        
        keyboard = get_main_keyboard()
        caption = get_main_caption()
        
        photo = get_banner_photo()
        
        if photo:
            try:
                await message.answer_photo(
                    photo=photo,
                    caption=caption,
                    reply_markup=keyboard
                )
                logger.info(f"Rasm yuborildi: user_id={user_id}")
            except Exception as e:
                logger.error(f"Rasm yuborishda xatolik: {e}")
                await message.answer(
                    caption,
                    reply_markup=keyboard
                )
        else:
            logger.info("Rasm topilmadi, matn yuborilmoqda")
            await message.answer(
                caption,
                reply_markup=keyboard
            )
            
    except Exception as e:
        logger.error(f"Start handlerda xatolik: {e}")
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
        )

# =============== ABOUT CALLBACK HANDLER ===============
@dp.callback_query(F.data == "about")
async def about(callback: CallbackQuery):
    try:
        # Orqaga qaytish tugmasi bilan about ma'lumoti
        about_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Orqaga",
                        callback_data="back_to_menu"
                    )
                ]
            ]
        )
        
        await callback.message.edit_text(
            "🇹🇷 TURK USTOZ\n\n"
            "Turk Ustoz — turk tilini o'rganish uchun yaratilgan "
            "zamonaviy ta'lim platformasi.\n\n"
            "📚 Platforma imkoniyatlari:\n"
            "• A1, A2, B1, B2 darajadagi darslar\n"
            "• Mavzular bo'yicha testlar\n"
            "• So'z yodlash mashqlari\n"
            "• Interaktiv Mini App\n"
            "• Grammatik qoidalar\n"
            "• Kundalik turkcha iboralar\n"
            "• O'quvchilar uchun qulay interfeys\n\n"
            "🎯 Maqsadimiz:\n"
            "Turk tilini o'rganishni oson, qiziqarli va samarali qilish.\n\n"
            "📱 Mini App imkoniyatlari:\n"
            "• Darslarni o'qish\n"
            "• Test ishlash\n"
            "• Natijalarni kuzatish\n"
            "• Yangi mavzularni o'rganish\n"
            "• Bilimingizni mustahkamlash\n\n"
            "🚀 Turk Ustoz bilan turk tilini oson va samarali o'rganing!",
            reply_markup=about_keyboard
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"About handlerda xatolik: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)

# =============== BACK TO MENU HANDLER ===============
@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        keyboard = get_main_keyboard()
        caption = get_main_caption()
        
        # Rasmni qayta yuklash
        photo = get_banner_photo()
        
        # Eski xabarni o'chirish
        await callback.message.delete()
        
        if photo:
            try:
                await callback.message.answer_photo(
                    photo=photo,
                    caption=caption,
                    reply_markup=keyboard
                )
            except Exception as e:
                logger.error(f"Rasm yuborishda xatolik (back): {e}")
                await callback.message.answer(
                    caption,
                    reply_markup=keyboard
                )
        else:
            await callback.message.answer(
                caption,
                reply_markup=keyboard
            )
        
        await callback.answer()
    except Exception as e:
        logger.error(f"Back to menu handlerda xatolik: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)

# =============== MAXSUS SO'Z UCHUN HANDLER (FAQAT ADMIN) ===============
@dp.message()
async def handle_special_word(message: Message):
    """Handle specific word '1Javohir2005' - faqat admin uchun"""
    try:
        user_id = message.from_user.id
        text = message.text.lower() if message.text else ""
        
        if "1javohir2005" in text or "1javohir" in text:
            if user_id == ADMIN_USER_ID:
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
                await message.reply(
                    "🔒 Bu maxfiy ma'lumot!\n"
                    "Faqat administrator ko'ra oladi."
                )
            return
        
        await message.answer(
            "❓ Iltimos, /start buyrug'ini bosing yoki tugmalardan foydalaning."
        )
    except Exception as e:
        logger.error(f"Special word handlerda xatolik: {e}")

# =============== MAIN ===============
async def main():
    logger.info("🤖 Bot ishga tushmoqda...")
    
    if os.path.exists("welcome.jpg"):
        file_size = os.path.getsize("welcome.jpg")
        logger.info(f"✅ welcome.jpg topildi. Hajmi: {file_size} bayt")
        if file_size > 20 * 1024 * 1024:
            logger.warning("⚠️ Rasm hajmi 20MB dan katta!")
    else:
        logger.warning("⚠️ welcome.jpg topilmadi!")
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot ishga tushishda xatolik: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
