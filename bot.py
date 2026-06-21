import os
import logging
import sys
import asyncio
import signal
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    WebAppInfo,
    InputFile
)
from aiogram import F
from aiogram.exceptions import TelegramNetworkError, TelegramConflictError

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

# Botni webhook o'chirib ishga tushiramiz
bot = Bot(token=TOKEN)
dp = Dispatcher()

# =============== CONSTANTS ===============
ADMIN_USER_ID = 8735290324
BANNER_FILE = "welcome.jpg"

# =============== FUNCTIONS ===============

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

async def send_banner(message: Message, caption: str, reply_markup=None):
    """Banner rasmni yuborish"""
    try:
        if os.path.exists(BANNER_FILE):
            logger.info("Rasm yuborilmoqda...")
            photo = InputFile(BANNER_FILE)
            
            await message.answer_photo(
                photo=photo,
                caption=caption,
                reply_markup=reply_markup
            )
            logger.info("✅ Rasm yuborildi!")
            return True
    except Exception as e:
        logger.error(f"Rasm yuborishda xatolik: {e}")
    
    # Fallback - matn yuborish
    logger.warning("Rasm yuborib bo'lmadi, matn yuborilmoqda...")
    await message.answer(
        caption,
        reply_markup=reply_markup
    )
    return False

# =============== HANDLERS ===============

@dp.message(CommandStart())
async def start(message: Message):
    try:
        user_id = message.from_user.id
        logger.info(f"Start komandasi: user_id={user_id}")
        
        keyboard = get_main_keyboard()
        caption = get_main_caption()
        
        await send_banner(message, caption, keyboard)
            
    except Exception as e:
        logger.error(f"Start handlerda xatolik: {e}")
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos, /start buyrug'ini qayta bosing."
        )

@dp.callback_query(F.data == "about")
async def about(callback: CallbackQuery):
    try:
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
            "🚀 Turk Ustoz bilan turk tilini oson va samarali o'rganing!",
            reply_markup=about_keyboard
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"About handlerda xatolik: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    try:
        keyboard = get_main_keyboard()
        caption = get_main_caption()
        
        await callback.message.delete()
        await send_banner(callback.message, caption, keyboard)
        await callback.answer()
    except Exception as e:
        logger.error(f"Back to menu handlerda xatolik: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)

@dp.message()
async def handle_special_word(message: Message):
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

# =============== SHUTDOWN HANDLER ===============
async def shutdown(loop, signal=None):
    """Botni to'g'ri o'chirish"""
    if signal:
        logger.info(f"Received exit signal {signal.name}...")
    
    logger.info("Bot to'xtatilmoqda...")
    
    # Bot sessionni to'g'ri yopish
    await bot.session.close()
    
    # Pollingni to'xtatish
    await dp.stop_polling()
    
    logger.info("Bot to'xtatildi!")

# =============== MAIN ===============

async def main():
    logger.info("🤖 Bot ishga tushmoqda...")
    
    # Fayl mavjudligini tekshirish
    if os.path.exists(BANNER_FILE):
        file_size = os.path.getsize(BANNER_FILE)
        logger.info(f"✅ {BANNER_FILE} topildi. Hajmi: {file_size} bayt ({file_size / 1024:.2f} KB)")
        
        if file_size > 20 * 1024 * 1024:
            logger.warning(f"⚠️ Rasm hajmi 20MB dan katta!")
    else:
        logger.warning(f"⚠️ {BANNER_FILE} topilmadi!")
    
    # Webhook'ni o'chirish (eski instance'larni to'xtatish uchun)
    try:
        logger.info("Webhook'ni o'chirish...")
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook o'chirildi!")
    except Exception as e:
        logger.error(f"Webhook o'chirishda xatolik: {e}")
    
    # Signal handler'lar
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig,
            lambda s=sig: asyncio.create_task(shutdown(loop, s))
        )
    
    # Botni polling bilan ishga tushirish
    try:
        await dp.start_polling(bot)
    except TelegramConflictError as e:
        logger.error(f"Conflict xatosi: {e}")
        logger.info("Bot boshqa instance'da ishlayapti. 5 soniya kutib qayta urinaman...")
        await asyncio.sleep(5)
        # Webhook'ni qayta o'chirish
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot ishga tushishda xatolik: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi!")
