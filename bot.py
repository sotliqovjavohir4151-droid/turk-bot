import asyncio
import os
import sqlite3
from datetime import datetime
from contextlib import contextmanager
import logging
import sys
import io
import aiohttp
import base64

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    WebAppInfo,
    FSInputFile,  # FSInputFile ishlatamiz
    BufferedInputFile
)
from aiogram.client.default import DefaultBotProperties
from aiohttp import web
from aiogram.exceptions import TelegramNetworkError

# =============== LOGGING ===============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# =============== CONFIG ===============
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.error("❌ BOT_TOKEN topilmadi!")
    sys.exit(1)

# Botni sozlash
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode="HTML",
    ),
    timeout=120,  # Timeoutni oshiramiz
)

dp = Dispatcher()

# =============== ADMIN USER ID ===============
ADMIN_USER_ID = 8735290324

# =============== DATABASE ===============
DB_PATH = "users.db"

# =============== RASM URL ===============
# O'zingizning rasmingiz URL manzilini qo'ying
BANNER_IMAGE_URL = "https://telegra.ph/file/your-image.jpg"  # <-- URL ni o'zgartiring

# Agar URL bo'lmasa, quyidagi BASE64 dan foydalaning
# BASE64 kodni shu yerga qo'ying (men tayyorlab beraman)
BANNER_IMAGE_BASE64 = ""

# =============== DATABASE FUNCTIONS ===============
@contextmanager
def get_db_connection():
    """Database connection context manager"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Create tables if they don't exist"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                username TEXT,
                full_name TEXT,
                language_code TEXT,
                is_premium BOOLEAN DEFAULT 0,
                joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_interactions INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER PRIMARY KEY,
                commands_used INTEGER DEFAULT 0,
                web_app_opened INTEGER DEFAULT 0,
                about_viewed INTEGER DEFAULT 0,
                channel_visited INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        logger.info("✅ Database initialized")

def add_or_update_user(message: Message):
    """Add new user or update existing user"""
    user = message.from_user
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user.id,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute('''
                UPDATE users 
                SET first_name = ?,
                    last_name = ?,
                    username = ?,
                    full_name = ?,
                    language_code = ?,
                    is_premium = ?,
                    last_active = CURRENT_TIMESTAMP,
                    total_interactions = total_interactions + 1
                WHERE user_id = ?
            ''', (
                user.first_name,
                user.last_name,
                user.username,
                user.full_name,
                user.language_code,
                1 if user.is_premium else 0,
                user.id
            ))
        else:
            cursor.execute('''
                INSERT INTO users (
                    user_id, first_name, last_name, username, 
                    full_name, language_code, is_premium, joined_date, total_interactions
                ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1)
            ''', (
                user.id,
                user.first_name,
                user.last_name,
                user.username,
                user.full_name,
                user.language_code,
                1 if user.is_premium else 0
            ))
            
            cursor.execute('''
                INSERT OR IGNORE INTO user_stats (user_id) VALUES (?)
            ''', (user.id,))
        
        conn.commit()

def log_activity(user_id: int, action: str):
    """Log user activity"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_activity (user_id, action) VALUES (?, ?)
            ''', (user_id, action))
            conn.commit()
    except Exception as e:
        logger.error(f"Error logging activity: {e}")

def update_stats(user_id: int, stat_field: str):
    """Update user statistics"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM user_stats WHERE user_id = ?', (user_id,))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute('INSERT INTO user_stats (user_id) VALUES (?)', (user_id,))
            
            cursor.execute(f'''
                UPDATE user_stats 
                SET {stat_field} = {stat_field} + 1
                WHERE user_id = ?
            ''', (user_id,))
            conn.commit()
    except Exception as e:
        logger.error(f"Error updating stats: {e}")

def get_user_info(user_id: int):
    """Get user information from database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('INSERT OR IGNORE INTO user_stats (user_id) VALUES (?)', (user_id,))
        conn.commit()
        
        cursor.execute('''
            SELECT 
                u.*,
                COALESCE(s.commands_used, 0) as commands_used,
                COALESCE(s.web_app_opened, 0) as web_app_opened,
                COALESCE(s.about_viewed, 0) as about_viewed,
                COALESCE(s.channel_visited, 0) as channel_visited
            FROM users u
            LEFT JOIN user_stats s ON u.user_id = s.user_id
            WHERE u.user_id = ?
        ''', (user_id,))
        return cursor.fetchone()

def get_user_activity(user_id: int, limit: int = 5):
    """Get user's recent activity"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT action, action_date 
            FROM user_activity 
            WHERE user_id = ? 
            ORDER BY action_date DESC 
            LIMIT ?
        ''', (user_id, limit))
        return cursor.fetchall()

def get_all_users_stats():
    """Get statistics for all users (admin only)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                u.user_id,
                u.first_name,
                u.username,
                u.joined_date,
                u.last_active,
                u.total_interactions,
                COALESCE(s.commands_used, 0) as commands_used,
                COALESCE(s.web_app_opened, 0) as web_app_opened,
                COALESCE(s.about_viewed, 0) as about_viewed,
                COALESCE(s.channel_visited, 0) as channel_visited
            FROM users u
            LEFT JOIN user_stats s ON u.user_id = s.user_id
            ORDER BY u.joined_date DESC
        ''')
        return cursor.fetchall()

# =============== RASMNI YUKLASH FUNKSIYASI ===============
async def download_image(url):
    """Rasmni URL dan yuklash"""
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    return image_data
                else:
                    logger.error(f"Rasm yuklanmadi: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Rasm yuklash xatosi: {e}")
        return None

async def get_banner_image():
    """Rasmni olish (URL yoki BASE64 dan)"""
    try:
        # 1-usul: URL dan
        if BANNER_IMAGE_URL and BANNER_IMAGE_URL.startswith('http'):
            image_data = await download_image(BANNER_IMAGE_URL)
            if image_data:
                # Vaqtinchalik faylga yozamiz
                temp_path = "temp_banner.jpg"
                with open(temp_path, 'wb') as f:
                    f.write(image_data)
                return FSInputFile(temp_path)
        
        # 2-usul: BASE64 dan
        if BANNER_IMAGE_BASE64:
            image_data = base64.b64decode(BANNER_IMAGE_BASE64)
            temp_path = "temp_banner.jpg"
            with open(temp_path, 'wb') as f:
                f.write(image_data)
            return FSInputFile(temp_path)
        
        # 3-usul: Mahalliy fayl
        if os.path.exists("turk_ustoz_banner.jpg"):
            return FSInputFile("turk_ustoz_banner.jpg")
        
        return None
    except Exception as e:
        logger.error(f"Rasm tayyorlash xatosi: {e}")
        return None

# =============== BOT HANDLERS ===============

def get_main_keyboard():
    """Get main menu keyboard"""
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
                    text="📊 Mening statistikam",
                    callback_data="my_stats"
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

@dp.message(CommandStart())
async def start(message: Message):
    try:
        user_id = message.from_user.id
        
        # Add/update user
        add_or_update_user(message)
        log_activity(user_id, "start_command")
        update_stats(user_id, "commands_used")
        
        keyboard = get_main_keyboard()
        caption = (
            f"🇹🇷 Turk Ustoz botiga xush kelibsiz, {message.from_user.first_name}🍃! 👋\n\n"
            "📚 Turk tilini o‘rganish uchun zamonaviy platforma.\n\n"
            "✅ Darslar\n"
            "✅ Testlar\n"
            "✅ So‘z yodlash mashqlari\n"
            "✅ Interaktiv Mini App\n"
            "✅ Loyihaga kirish uchun \"Ilovani ochish\" tugmasini bosing\n\n"
            "Kerakli bo‘limni tanlang 👇"
        )
        
        # Rasmni yukashga harakat qilamiz
        try:
            banner_image = await get_banner_image()
            
            if banner_image:
                await message.answer_photo(
                    photo=banner_image,
                    caption=caption,
                    reply_markup=keyboard
                )
                # Vaqtinchalik faylni tozalash
                if os.path.exists("temp_banner.jpg"):
                    os.remove("temp_banner.jpg")
            else:
                # Rasm yo'q bo'lsa matn yuborish
                await message.answer(
                    caption,
                    reply_markup=keyboard
                )
        except Exception as e:
            logger.error(f"Rasm yuborish xatosi: {e}")
            # Xatolik bo'lsa matn yuboramiz
            await message.answer(
                caption,
                reply_markup=keyboard
            )
            
    except TelegramNetworkError as e:
        logger.error(f"Telegram tarmoq xatosi: {e}")
        await message.answer("⏳ Kechirasiz, texnik muammo yuz berdi. Iltimos, birozdan keyin qayta urinib ko'ring.")
    except Exception as e:
        logger.error(f"Kutilmagan xatolik: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, /start buyrug'ini qayta bosing.")

# =============== MAXSUS SO'Z UCHUN HANDLER ===============
@dp.message()
async def handle_special_word(message: Message):
    """Handle specific word '1Javohir2005'"""
    try:
        user_id = message.from_user.id
        text = message.text.lower() if message.text else ""
        
        # Check for the special word
        if "1javohir2005" in text or "1javohir" in text:
            log_activity(user_id, "special_word_triggered")
            
            # Check if user is admin
            if user_id == ADMIN_USER_ID:
                all_stats = get_all_users_stats()
                
                if all_stats:
                    stats_text = "📊 **BARCHA FOYDALANUVCHILAR STATISTIKASI**\n\n"
                    stats_text += f"👥 Jami foydalanuvchilar: {len(all_stats)}\n\n"
                    
                    for i, user in enumerate(all_stats[:20], 1):
                        stats_text += (
                            f"{i}. 👤 {user['first_name']}\n"
                            f"   🔹 @{user['username'] or 'mavjud emas'}\n"
                            f"   📅 Qo'shilgan: {user['joined_date'][:10]}\n"
                            f"   💬 Muloqotlar: {user['total_interactions']}\n"
                            f"   📈 /start: {user['commands_used']} | Web: {user['web_app_opened']}\n\n"
                        )
                    
                    if len(all_stats) > 20:
                        stats_text += f"... va yana {len(all_stats) - 20} ta foydalanuvchi"
                    
                    await message.reply(stats_text)
                else:
                    await message.reply("❌ Hali foydalanuvchilar yo'q!")
            else:
                await message.reply(
                    "🔒 Bu maxfiy ma'lumot!\n"
                    "Faqat administrator ko'ra oladi.\n\n"
                    "Siz o'z statistikangizni 📊 Mening statistikam tugmasi orqali ko'rishingiz mumkin."
                )
            return
        
        # Handle other messages
        await message.answer(
            "❓ Iltimos, /start buyrug'ini bosing yoki tugmalardan foydalaning."
        )
    except Exception as e:
        logger.error(f"Xatolik: {e}")
        await message.answer("❌ Xatolik yuz berdi.")

@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Return to main menu"""
    try:
        user_id = callback.from_user.id
        log_activity(user_id, "back_to_menu")
        
        keyboard = get_main_keyboard()
        caption = (
            "🇹🇷 Turk Ustoz botiga xush kelibsiz! 👋\n\n"
            "📚 Turk tilini o‘rganish uchun zamonaviy platforma.\n\n"
            "✅ Darslar\n"
            "✅ Testlar\n"
            "✅ So‘z yodlash mashqlari\n"
            "✅ Interaktiv Mini App\n\n"
            "Kerakli bo‘limni tanlang 👇"
        )
        
        # Delete old message
        await callback.message.delete()
        
        # Rasmni yukashga harakat qilamiz
        try:
            banner_image = await get_banner_image()
            
            if banner_image:
                await callback.message.answer_photo(
                    photo=banner_image,
                    caption=caption,
                    reply_markup=keyboard
                )
                if os.path.exists("temp_banner.jpg"):
                    os.remove("temp_banner.jpg")
            else:
                await callback.message.answer(
                    caption,
                    reply_markup=keyboard
                )
        except Exception as e:
            logger.error(f"Rasm yuborish xatosi: {e}")
            await callback.message.answer(
                caption,
                reply_markup=keyboard
            )
        
        await callback.answer()
    except Exception as e:
        logger.error(f"Back to menu xatolik: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)

@dp.callback_query(lambda c: c.data == "about")
async def about(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        log_activity(user_id, "about_viewed")
        update_stats(user_id, "about_viewed")
        
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
            "🚀 Turk Ustoz bilan turk tilini oson va samarali o‘rganing!"
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"About xatolik: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)

@dp.callback_query(lambda c: c.data == "my_stats")
async def my_stats(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        log_activity(user_id, "view_stats")
        update_stats(user_id, "commands_used")
        
        user_info = get_user_info(user_id)
        recent_activity = get_user_activity(user_id)
        
        if user_info:
            try:
                joined_date = datetime.strptime(user_info['joined_date'], '%Y-%m-%d %H:%M:%S')
                last_active = datetime.strptime(user_info['last_active'], '%Y-%m-%d %H:%M:%S')
            except:
                joined_date = datetime.now()
                last_active = datetime.now()
            
            stats_text = (
                f"📊 Sizning statistikangiz\n\n"
                f"👤 Ism: {user_info['first_name']}\n"
                f"🔹 Username: @{user_info['username'] or 'mavjud emas'}\n"
                f"📅 Qo'shilgan sana: {joined_date.strftime('%d.%m.%Y %H:%M')}\n"
                f"🕐 Oxirgi faollik: {last_active.strftime('%d.%m.%Y %H:%M')}\n"
                f"💬 Umumiy muloqotlar: {user_info['total_interactions']}\n\n"
                f"📈 Faoliyat ko'rsatkichlari:\n"
                f"• /start buyrug'i: {user_info['commands_used'] or 0} marta\n"
                f"• Web App ochilgan: {user_info['web_app_opened'] or 0} marta\n"
                f"• Bot haqida ko'rilgan: {user_info['about_viewed'] or 0} marta\n"
                f"• Kanalga o'tilgan: {user_info['channel_visited'] or 0} marta\n"
            )
            
            if recent_activity and len(recent_activity) > 0:
                stats_text += "\n🔄 So'nggi faollik:\n"
                for activity in recent_activity[:5]:
                    try:
                        date = datetime.strptime(activity['action_date'], '%Y-%m-%d %H:%M:%S')
                        stats_text += f"• {activity['action']} - {date.strftime('%d.%m %H:%M')}\n"
                    except:
                        stats_text += f"• {activity['action']}\n"
            
            await callback.message.answer(stats_text)
        else:
            add_or_update_user(callback.message)
            await callback.message.answer(
                "📊 Sizning statistikangiz hali yaratilmagan.\n"
                "Iltimos, avval /start buyrug'ini bosing!"
            )
        
        await callback.answer()
    except Exception as e:
        logger.error(f"My stats xatolik: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)

# Handle Web App opening
@dp.message(lambda message: message.web_app_data is not None)
async def web_app_data_handler(message: Message):
    try:
        user_id = message.from_user.id
        log_activity(user_id, "web_app_opened")
        update_stats(user_id, "web_app_opened")
        
        await message.answer("✅ Web App ma'lumotlari qabul qilindi!")
    except Exception as e:
        logger.error(f"Web app xatolik: {e}")

# =============== WEB SERVER ===============

async def health(request):
    return web.Response(text="Turk Ustoz Bot ishlayapti!")

async def stats_api(request):
    """API endpoint to get user statistics"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                COUNT(*) as total_users,
                SUM(CASE WHEN joined_date >= datetime('now', '-1 day') THEN 1 ELSE 0 END) as new_today
            FROM users
        ''')
        stats = cursor.fetchone()
        return web.json_response({
            'total_users': stats['total_users'],
            'new_users_today': stats['new_today']
        })

# =============== MAIN ===============

async def main():
    # Initialize database
    init_db()
    logger.info(f"👑 Admin ID: {ADMIN_USER_ID}")
    
    # Web server setup
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/stats", stats_api)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"🌐 Server {port} portda ishga tushdi")
    logger.info(f"🤖 Bot ishga tushdi...")
    
    # Start bot polling with retry
    while True:
        try:
            await dp.start_polling(bot)
        except TelegramNetworkError as e:
            logger.error(f"Bot polling xatosi: {e}")
            await asyncio.sleep(10)
            continue
        except Exception as e:
            logger.error(f"Kutilmagan xatolik: {e}")
            await asyncio.sleep(5)
            continue

if __name__ == "__main__":
    asyncio.run(main())
