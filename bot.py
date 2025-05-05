import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ParseMode

API_TOKEN = '7900733074:AAGvNGqkx00styCTJYqvJRV5B9Kiw5XLPJQ'
CHANNEL_USERNAME = 'svetvmashine'

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
router = Router()
dp = Dispatcher()
dp.include_router(router)

check_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_sub")]
    ]
)

# 📎 Получение file_id
@router.message(F.document)
async def get_file_id(message: Message):
    file_id = message.document.file_id
    await message.answer(f"📎 file_id: <code>{file_id}</code>")
@router.message(F.document)
async def get_file_id(message: Message):
    file_id = message.document.file_id
    await message.answer(f"📎 document file_id: <code>{file_id}</code>")

@router.message(F.audio)
async def get_audio_file_id(message: Message):
    file_id = message.audio.file_id
    await message.answer(f"🎵 audio file_id: <code>{file_id}</code>")

# 📩 /start
@router.message(F.text == "/start")
async def cmd_start(message: Message):
    text = (
        "Привет! ✨\n\n"
        "Чтобы получить медитацию, пожалуйста, подпишитесь на канал:\n"
        f"👉 <a href='https://t.me/{CHANNEL_USERNAME}'>@{CHANNEL_USERNAME}</a>\n\n"
        "После этого нажмите кнопку ниже:"
    )
    await message.answer(text, reply_markup=check_button)

# 🔍 Проверка подписки
@router.callback_query(F.data == "check_sub")
async def check_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id

    try:
        member = await bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        if member.status in ("member", "administrator", "creator"):
            await callback.message.answer("🎉 Спасибо за подписку! Вот ваша медитация:")
            await callback.message.answer_document("CQACAgIAAxkBAAMeaBcf2YDdLQHYrvrCq_kV56zy1UUAArtwAAKY8cBIl96ssS0AAXEuNgQ")
        else:
            await callback.message.answer("😔 Пожалуйста, подпишитесь на канал сначала.")
    except TelegramBadRequest:
        await callback.message.answer("⚠️ Не удалось проверить подписку. Попробуйте позже.")

# 🏁 Запуск
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
