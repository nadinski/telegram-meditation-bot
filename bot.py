import asyncio
import logging
import datetime
from collections import defaultdict
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

API_TOKEN = '7900733074:AAHe06fcSukREMlysbbHnw2bHxzQv7Vyjmw'
CHANNEL_USERNAME = 'svetvmashine'
ADMIN_ID = 348493357  # ЗАМЕНИТЕ НА ВАШ ID В TELEGRAM

# Хранилище статистики (в памяти)
user_stats = defaultdict(lambda: {'start_count': 0, 'last_active': None, 'subscription_checked': 0})
bot_stats = {'total_users': 0, 'active_today': 0}

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
router = Router()
dp = Dispatcher()
dp.include_router(router)

check_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_sub")]
    ]
)

def update_stats(user_id):
    """Обновляем статистику пользователя"""
    now = datetime.datetime.now()
    
    # Первый раз пользователь?
    if user_stats[user_id]['last_active'] is None:
        bot_stats['total_users'] += 1
    
    # Активен сегодня?
    if user_stats[user_id]['last_active'] and (now - user_stats[user_id]['last_active']).days >= 1:
        bot_stats['active_today'] += 1
    elif user_stats[user_id]['last_active'] is None:
        bot_stats['active_today'] += 1
    
    user_stats[user_id]['start_count'] += 1
    user_stats[user_id]['last_active'] = now

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    update_stats(user_id)
    
    text = (
        "Привет! ✨\n\n"
        "Чтобы получить медитацию, пожалуйста, подпишитесь на канал:\n"
        f"👉 <a href='https://t.me/{CHANNEL_USERNAME}'>@{CHANNEL_USERNAME}</a>\n\n"
        "После этого нажмите кнопку ниже:"
    )
    await message.answer(text, reply_markup=check_button)

@router.callback_query(F.data == "check_sub")
async def check_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_stats[user_id]['subscription_checked'] += 1
    
    try:
        member = await bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        if member.status in ("member", "administrator", "creator"):
            await callback.message.answer("🎉 Спасибо за подписку! Вот ваша медитация:")
            await callback.message.answer_document("CQACAgIAAxkBAAMeaBcf2YDdLQHYrvrCq_kV56zy1UUAArtwAAKY8cBIl96ssS0AAXEuNgQ")
        else:
            await callback.message.answer("😔 Пожалуйста, подпишитесь на канал сначала.")
    except TelegramBadRequest:
        await callback.message.answer("⚠️ Не удалось проверить подписку. Попробуйте позже.")

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Команда статистики только для админа"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас нет доступа к этой команде")
        return
    
    now = datetime.datetime.now()
    active_today = sum(1 for stats in user_stats.values() 
                      if stats['last_active'] and 
                      (now - stats['last_active']).days < 1)
    
    successful_checks = sum(1 for stats in user_stats.values() 
                           if stats['subscription_checked'] > 0)
    
    stats_text = (
        "📊 <b>Статистика бота</b>\n\n"
        f"👥 <b>Всего пользователей:</b> {bot_stats['total_users']}\n"
        f"🔔 <b>Активных за сегодня:</b> {active_today}\n"
        f"✅ <b>Проверок подписки:</b> {successful_checks}\n"
        f"🕐 <b>Последнее обновление:</b> {now.strftime('%d.%m.%Y %H:%M')}\n\n"
        f"<i>Статистика обновляется в реальном времени</i>"
    )
    
    await message.answer(stats_text)

@router.message(Command("user_stats"))
async def cmd_user_stats(message: Message):
    """Статистика конкретного пользователя для админа"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if not message.reply_to_message:
        await message.answer("❌ Ответьте на сообщение пользователя чтобы посмотреть его статистику")
        return
    
    user_id = message.reply_to_message.from_user.id
    stats = user_stats[user_id]
    
    user_info = (
        f"📈 <b>Статистика пользователя</b>\n\n"
        f"🆔 ID: {user_id}\n"
        f"👤 Имя: {message.reply_to_message.from_user.full_name}\n"
        f"🚀 Запусков бота: {stats['start_count']}\n"
        f"✅ Проверок подписки: {stats['subscription_checked']}\n"
        f"🕐 Последняя активность: {stats['last_active'].strftime('%d.%m.%Y %H:%M') if stats['last_active'] else 'Никогда'}"
    )
    
    await message.answer(user_info)
@router.message(Command("users"))
async def cmd_users(message: Message):
    """Список всех пользователей бота (для админа)"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if not user_stats:
        await message.answer("📭 Еще нет пользователей")
        return
    
    users_list = "👥 <b>Пользователи бота:</b>\n\n"
    for user_id, stats in list(user_stats.items())[:50]:  # Первые 50 чтобы не превысить лимит сообщения
        users_list += f"🆔 {user_id} - 🚀 {stats['start_count']} раз\n"
    
    await message.answer(users_list)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
