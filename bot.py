import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

API_TOKEN = '7900733074:AAHe06fcSukREMlysbbHnw2bHxzQv7Vyjmw'
CHANNEL_USERNAME = 'svetvmashine'
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = "https://nadinski.pythonanywhere.com" + WEBHOOK_PATH  # Замените на ваш username

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
router = Router()
dp = Dispatcher()
dp.include_router(router)

check_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_sub")]
    ]
)

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

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)

app = web.Application()
webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
webhook_requests_handler.register(app, path=WEBHOOK_PATH)
setup_application(app, dp, bot=bot)
dp.startup.register(on_startup)
