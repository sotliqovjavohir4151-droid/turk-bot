from aiogram.types import (
Message,
InlineKeyboardMarkup,
InlineKeyboardButton
)

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

text = (
    "🇹🇷 Turk Ustoz botiga xush kelibsiz!\n\n"
    "📚 Turk tilini zamonaviy usulda o‘rganing.\n\n"
    "Bot imkoniyatlari:\n"
    "• Interaktiv darslar\n"
    "• Mavzular bo‘yicha testlar\n"
    "• So‘z yodlash mashqlari\n"
    "• Mini App orqali o‘rganish\n"
    "• Bosqichma-bosqich A1 → B2 kurslari\n\n"
    "👇 Kerakli bo‘limni tanlang"
)

await message.answer(
    text,
    reply_markup=keyboard
)

@dp.message(lambda message: message.text == "ℹ️ Bot haqida")
async def about(message: Message):
await message.answer(
"🇹🇷 Turk Ustoz haqida\n\n"
"Turk Ustoz — o‘zbek tilida turk tilini o‘rganish uchun "
"yaratilgan ta’lim platformasi.\n\n"
"Platformada:\n"
"📚 Darslar\n"
"📝 Testlar\n"
"🎯 Mashqlar\n"
"📖 Lug‘atlar\n"
"🏆 Natijalar tizimi\n\n"
"Maqsad — turk tilini o‘rganishni sodda, qulay va samarali qilish.\n\n"
"Loyiha muallifi: @sotiiqov"
)
