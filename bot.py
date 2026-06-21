import os
import logging
import sys
import asyncio
import signal
import sqlite3
from datetime import datetime
from contextlib import contextmanager
from aiogram import Bot, Dispatcher
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
from aiogram.exceptions import TelegramNetworkError, TelegramConflictError
from aiohttp import web

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

# =============== CONSTANTS ===============
ADMIN_USER_ID = 8735290324
BANNER_FILE = "welcome.jpg"
DB_PATH = "users.db"

# =============== DATABASE ===============
@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                username TEXT,
                joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        logger.info("✅ Database initialized")

def add_user(message: Message):
    user = message.from_user
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user.id,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute('''
                INSERT INTO users (user_id, first_name, username)
                VALUES (?, ?, ?)
            ''', (user.id, user.first_name, user.username))
            conn.commit()
            logger.info(f"✅ Yangi foydalanuvchi qo'shildi: {user.id}")

def get_total_users():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM users')
        result = cursor.fetchone()
        return result['count'] if result else 0

def get_all_users():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, first_name, username, joined_date
            FROM users
            ORDER BY joined_date DESC
        ''')
        return cursor.fetchall()

# =============== ASOSIY FUNKSIYALAR ===============

def get_main_keyboard():
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

def get_about_text():
    return (
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
        "🚀 Turk Ustoz bilan turk tilini oson va samarali o'rganing!"
    )

async def send_banner(message: Message, caption: str, reply_markup=None):
    try:
        if os.path.exists(BANNER_FILE):
            photo = FSInputFile(BANNER_FILE)
            await message.answer_photo(
                photo=photo,
                caption=caption,
                reply_markup=reply_markup
            )
            logger.info("✅ Rasm yuborildi!")
            return True
    except Exception as e:
        logger.error(f"Rasm yuborishda xatolik: {e}")
    
    await message.answer(caption, reply_markup=reply_markup)
    return False

# =============== HANDLERLAR ===============

@dp.message(CommandStart())
async def start(message: Message):
    try:
        user_id = message.from_user.id
        logger.info(f"Start komandasi: user_id={user_id}")
        
        # Foydalanuvchini bazaga qo'shish
        add_user(message)
        
        keyboard = get_main_keyboard()
        caption = get_main_caption()
        
        await send_banner(message, caption, keyboard)
            
    except Exception as e:
        logger.error(f"Start handlerda xatolik: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, /start buyrug'ini qayta bosing.")

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
        
        # Xabar turini tekshirish
        if callback.message.text:
            await callback.message.edit_text(
                get_about_text(),
                reply_markup=about_keyboard
            )
        else:
            # Agar rasm bo'lsa, yangi xabar yuboramiz
            await callback.message.delete()
            await callback.message.answer(
                get_about_text(),
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
                # Haqiqiy statistikani olish
                total_users = get_total_users()
                all_users = get_all_users()
                
                stats_text = f"📊 **BARCHA FOYDALANUVCHILAR STATISTIKASI**\n\n"
                stats_text += f"👥 Jami foydalanuvchilar: {total_users} ta\n\n"
                stats_text += "📋 **Foydalanuvchilar ro'yxati:**\n"
                
                if all_users:
                    for i, user in enumerate(all_users, 1):
                        username = f"@{user['username']}" if user['username'] else "username yo'q"
                        stats_text += f"{i}. {user['first_name']} - {username}\n"
                        stats_text += f"   📅 Qo'shilgan: {user['joined_date'][:10]}\n"
                else:
                    stats_text += "Hali foydalanuvchilar yo'q"
                
                await message.reply(stats_text)
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

# =============== WEB SERVER ===============
async def health_check(request):
    return web.Response(text="Bot ishlayapti!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"🌐 Web server {port} portda ishga tushdi")
    return runner

# =============== SHUTDOWN ===============
async def shutdown(loop, signal=None):
    if signal:
        logger.info(f"Received exit signal {signal.name}...")
    
    logger.info("Bot to'xtatilmoqda...")
    await bot.session.close()
    await dp.stop_polling()
    logger.info("Bot to'xtatildi!")

# =============== MAIN ===============

async def main():
    logger.info("🤖 Bot ishga tushmoqda...")
    
    # Database initializatsiya
    init_db()
    
    # Faylni tekshirish
    if os.path.exists(BANNER_FILE):
        file_size = os.path.getsize(BANNER_FILE)
        logger.info(f"✅ {BANNER_FILE} topildi. Hajmi: {file_size} bayt")
    else:
        logger.warning(f"⚠️ {BANNER_FILE} topilmadi!")
    
    # Webhook'ni o'chirish
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook o'chirildi!")
    except Exception as e:
        logger.error(f"Webhook o'chirishda xatolik: {e}")
    
    # Signal handler
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(shutdown(loop, s))
            )
        except NotImplementedError:
            pass
    
    # Web serverni ishga tushirish
    try:
        web_runner = await start_web_server()
    except Exception as e:
        logger.error(f"Web server xatosi: {e}")
        web_runner = None
    
    # Botni ishga tushirish
    retry_count = 0
    max_retries = 5
    
    while retry_count < max_retries:
        try:
            await dp.start_polling(bot)
            break
        except TelegramConflictError as e:
            retry_count += 1
            logger.error(f"Conflict xatosi ({retry_count}/{max_retries}): {e}")
            await bot.delete_webhook(drop_pending_updates=True)
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Bot polling xatosi: {e}")
            break
    
    if web_runner:
        await web_runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi!")
