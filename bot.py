import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ParseMode
from aiogram.filters import Command

API_TOKEN = '7900733074:AAHe06fcSukREMlysbbHnw2bHxzQv7Vyjmw'
CHANNEL_USERNAME = 'svetvmashine'

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

check_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_sub")]
    ]
)

# 📩 /start команда
@dp.message(Command("start"))
async def cmd_start(message: Message):
    text = (
        "Привет! ✨\n\n"
        "Чтобы получить медитацию, пожалуйста, подпишитесь на канал:\n"
        f"👉 <a href='https://t.me/{CHANNEL_USERNAME}'>@{CHANNEL_USERNAME}</a>\n\n"
        "После этого нажмите кнопку ниже:"
    )
    await message.answer(text, reply_markup=check_button)

# 🔍 Проверка подписки
@dp.callback_query(F.data == "check_sub")
async def check_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id

    try:
        member = await bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        if member.status in ("member", "administrator", "creator"):
            await callback.message.answer("🎉 Спасибо за подписку! Вот ваша медитация:")
            await callback.message.answer_document("CQACAgIAAxkBAAMeaBcf2YDdLQHYrvrCq_kV56zy1UUAArtwAAKY8cBIl96ssS0AAXEuNgQ")
        else:
            await callback.message.answer("😔 Пожалуйста, подпишитесь на канал сначала.")
    except TelegramBadRequest as e:
        logging.error(f"Ошибка проверки подписки: {e}")
        await callback.message.answer("⚠️ Не удалось проверить подписку. Попробуйте позже.")

# 🏁 Запуск
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
