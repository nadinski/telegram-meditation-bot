import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ParseMode

API_TOKEN = '7900733074:AAFIhX9-YQz-Hvtec0j6CaU3mcIc4PKEpzQ'
CHANNEL_USERNAME = 'svetvmashine'  # без https://t.me/

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# 👇 Кнопка для проверки подписки
check_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_sub")]
    ]
)

# 📩 /start
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    text = (
        "Привет! ✨\n\n"
        "Чтобы получить медитацию, пожалуйста, подпишись на канал:\n"
        f"👉 <a href='https://t.me/{CHANNEL_USERNAME}'>@{CHANNEL_USERNAME}</a>\n\n"
        "После этого нажми кнопку ниже:"
    )
    await message.answer(text, reply_markup=check_button)

# 🔍 Проверка подписки
@dp.callback_query(F.data == "check_sub")
async def check_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id

    try:
        member = await bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        if member.status in ("member", "administrator", "creator"):
            await callback.message.answer("🎉 Спасибо за подписку! Вот твоя медитация:")
            await callback.message.answer_document(open("meditation.mp3", "rb"))
        else:
            await callback.message.answer("😔 Пожалуйста, подпишись на канал сначала.")
    except TelegramBadRequest:
        await callback.message.answer("⚠️ Не удалось проверить подписку. Попробуй позже.")

# 🏁 Запуск бота
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
