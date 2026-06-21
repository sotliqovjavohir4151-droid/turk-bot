import asyncio
import os
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
    WebAppInfo
)
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# =============== DATABASE ===============
DB_PATH = "users.db"

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
        
        # Users table
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
        
        # User statistics table
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
        
        # User activity log table
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

def add_or_update_user(message: Message):
    """Add new user or update existing user"""
    user = message.from_user
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user.id,))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing user
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
            # Insert new user
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
            
            # Create initial statistics for new user
            cursor.execute('''
                INSERT INTO user_stats (user_id) VALUES (?)
            ''', (user.id,))
        
        conn.commit()

def log_activity(user_id: int, action: str):
    """Log user activity"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_activity (user_id, action) VALUES (?, ?)
        ''', (user_id, action))
        conn.commit()

def update_stats(user_id: int, stat_field: str):
    """Update user statistics"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE user_stats 
            SET {stat_field} = {stat_field} + 1
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()

def get_user_info(user_id: int):
    """Get user information from database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                u.*,
                s.commands_used,
                s.web_app_opened,
                s.about_viewed,
                s.channel_visited
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

# =============== BOT HANDLERS ===============

@dp.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    
    # Add/update user
    add_or_update_user(message)
    log_activity(user_id, "start_command")
    update_stats(user_id, "commands_used")
    
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

    await message.answer(
        f"🇹🇷 Turk Ustoz botiga xush kelibsiz, {message.from_user.first_name}! 👋\n\n"
        "📚 Turk tilini o‘rganish uchun zamonaviy platforma.\n\n"
        "✅ Darslar\n"
        "✅ Testlar\n"
        "✅ So‘z yodlash mashqlari\n"
        "✅ Interaktiv Mini App\n"
        "✅ Loyihaga kirish uchun \"Ilovani ochish\" tugmasini bosing\n\n"
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=keyboard
    )

# =============== MAXSUS SO'Z UCHUN HANDLER ===============
@dp.message()
async def handle_special_word(message: Message):
    """Handle specific word '1Javohir2005'"""
    user_id = message.from_user.id
    text = message.text.lower() if message.text else ""
    
    # Check for the special word (case insensitive)
    if "1javohir2005" in text or "1javohir" in text:
        log_activity(user_id, "special_word_triggered")
        
        # Create special keyboard
        special_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="👨‍💻 Dasturchi bilan bog'lanish",
                        url="https://t.me/sotiiqov"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📊 Statistika",
                        callback_data="my_stats"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔙 Orqaga",
                        callback_data="back_to_menu"
                    )
                ]
            ]
        )
        
        await message.reply(
            "🌟 **JAVOHIR DEV** 🌟\n\n"
            "👨‍💻 Dasturchi: Javohir Sotliqov\n"
            "📱 Telegram: @sotiiqov\n"
            "💻 GitHub: github.com/javohirdev\n"
            "🚀 Loyiha: Turk Ustoz\n\n"
            "✨ Bu bot va web app Javohir tomonidan yaratilgan!\n"
            "💡 Har qanday savol va takliflar uchun bog'lanishingiz mumkin.",
            reply_markup=special_keyboard
        )
        return
    
    # Handle other messages
    await message.answer(
        "❓ Iltimos, /start buyrug'ini bosing yoki tugmalardan foydalaning."
    )

@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Return to main menu"""
    user_id = callback.from_user.id
    log_activity(user_id, "back_to_menu")
    
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
    
    await callback.message.edit_text(
        "🇹🇷 Turk Ustoz botiga xush kelibsiz! 👋\n\n"
        "📚 Turk tilini o‘rganish uchun zamonaviy platforma.\n\n"
        "✅ Darslar\n"
        "✅ Testlar\n"
        "✅ So‘z yodlash mashqlari\n"
        "✅ Interaktiv Mini App\n\n"
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "about")
async def about(callback: CallbackQuery):
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
        "📱 Mini App imkoniyatlari:\n"
        "• Darslarni o‘qish\n"
        "• Test ishlash\n"
        "• Natijalarni kuzatish\n"
        "• Yangi mavzularni o‘rganish\n"
        "• Bilimingizni mustahkamlash\n\n"
        "🚀 Turk Ustoz bilan turk tilini oson va samarali o‘rganing!"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "my_stats")
async def my_stats(callback: CallbackQuery):
    user_id = callback.from_user.id
    log_activity(user_id, "view_stats")
    update_stats(user_id, "commands_used")
    
    user_info = get_user_info(user_id)
    recent_activity = get_user_activity(user_id)
    
    if user_info:
        joined_date = datetime.strptime(user_info['joined_date'], '%Y-%m-%d %H:%M:%S')
        last_active = datetime.strptime(user_info['last_active'], '%Y-%m-%d %H:%M:%S')
        
        stats_text = (
            f"📊 Sizning statistikangiz\n\n"
            f"👤 Ism: {user_info['first_name']}\n"
            f"🔹 Username: @{user_info['username'] or 'mavjud emas'}\n"
            f"📅 Qo'shilgan sana: {joined_date.strftime('%d.%m.%Y %H:%M')}\n"
            f"🕐 Oxirgi faollik: {last_active.strftime('%d.%m.%Y %H:%M')}\n"
            f"💬 Umumiy muloqotlar: {user_info['total_interactions']}\n\n"
            f"📈 Faoliyat ko'rsatkichlari:\n"
            f"• /start buyrug'i: {user_info['commands_used']} marta\n"
            f"• Web App ochilgan: {user_info['web_app_opened']} marta\n"
            f"• Bot haqida ko'rilgan: {user_info['about_viewed']} marta\n"
            f"• Kanalga o'tilgan: {user_info['channel_visited']} marta\n"
        )
        
        if recent_activity:
            stats_text += "\n🔄 So'nggi faollik:\n"
            for activity in recent_activity:
                date = datetime.strptime(activity['action_date'], '%Y-%m-%d %H:%M:%S')
                stats_text += f"• {activity['action']} - {date.strftime('%d.%m %H:%M')}\n"
        
        await callback.message.answer(stats_text)
    else:
        await callback.message.answer("❌ Ma'lumot topilmadi!")
    
    await callback.answer()

# Handle Web App opening
@dp.message(lambda message: message.web_app_data is not None)
async def web_app_data_handler(message: Message):
    user_id = message.from_user.id
    log_activity(user_id, "web_app_opened")
    update_stats(user_id, "web_app_opened")
    
    # Process web app data if needed
    data = message.web_app_data.data
    await message.answer("✅ Web App ma'lumotlari qabul qilindi!")

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
    print("✅ Database initialized")
    
    # Web server setup
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/stats", stats_api)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Server {port} portda ishga tushdi")
    print(f"🤖 Bot ishga tushdi...")
    
    # Start bot polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
