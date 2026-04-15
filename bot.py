import asyncio
import logging
import datetime
from collections import defaultdict
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

API_TOKEN = '7900733074:AAHe06fcSukREMlysbbHnw2bHxzQv7Vyjmw'
CHANNEL_USERNAME = 'svetvmashine'
ADMIN_ID = 348493357
WEB_APP_URL = "https://nadinski.github.io/miniapp/"  # ЗАМЕНИТЕ НА ВАШ URL

# Хранилище данных пользователей
user_data = defaultdict(lambda: {
    'start_count': 0, 
    'last_active': None, 
    'subscription_checked': 0,
    'pending_action': None  # 'calculator' или 'meditation'
})
bot_stats = {'total_users': 0, 'active_today': 0}

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
router = Router()
dp = Dispatcher()
dp.include_router(router)

def get_main_menu(user_id):
    """Возвращает главное меню с кнопкой статистики только для админа"""
    buttons = [
        [InlineKeyboardButton(text="🧮 Калькулятор бюджета", callback_data="calculator")],
        [InlineKeyboardButton(text="🧘 Получить медитацию", callback_data="meditation")]
    ]
    
    # Добавляем кнопку статистики только для администратора
    if user_id == ADMIN_ID:
        buttons.append([InlineKeyboardButton(text="📊 Статистика бота", callback_data="stats")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Клавиатура проверки подписки
check_subscription_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_sub")],
        [InlineKeyboardButton(text="📺 Перейти в канал", url=f"https://t.me/{CHANNEL_USERNAME}")]
    ]
)

def update_stats(user_id):
    """Обновляем статистику пользователя"""
    now = datetime.datetime.now()
    
    if user_data[user_id]['last_active'] is None:
        bot_stats['total_users'] += 1
    
    if user_data[user_id]['last_active'] and (now - user_data[user_id]['last_active']).days >= 1:
        bot_stats['active_today'] += 1
    elif user_data[user_id]['last_active'] is None:
        bot_stats['active_today'] += 1
    
    user_data[user_id]['start_count'] += 1
    user_data[user_id]['last_active'] = now

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    update_stats(user_id)
    
    welcome_text = (
        "🌟 <b>Добро пожаловать!</b>\n\n"
        "Выберите нужный вариант:"
    )
    
    await message.answer(welcome_text, reply_markup=get_main_menu(user_id))

@router.callback_query(F.data == "calculator")
async def start_calculator(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data[user_id]['pending_action'] = 'calculator'
    
    text = (
        "🧮 <b>Калькулятор бюджета на сайт и рекламу</b>\n\n"
        "Чтобы использовать калькулятор, пожалуйста, подпишитесь на наш канал:\n"
        f"👉 <a href='https://t.me/{CHANNEL_USERNAME}'>@{CHANNEL_USERNAME}</a>\n\n"
        "После подписки нажмите кнопку проверки:"
    )
    
    await callback.message.edit_text(text, reply_markup=check_subscription_kb)

@router.callback_query(F.data == "meditation")
async def start_meditation(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data[user_id]['pending_action'] = 'meditation'
    
    text = (
        "🧘 <b>Получить медитацию</b>\n\n"
        "Чтобы получить медитацию, пожалуйста, подпишитесь на наш канал:\n"
        f"👉 <a href='https://t.me/{CHANNEL_USERNAME}'>@{CHANNEL_USERNAME}</a>\n\n"
        "После подписки нажмите кнопку проверки:"
    )
    
    await callback.message.edit_text(text, reply_markup=check_subscription_kb)

@router.callback_query(F.data == "check_sub")
async def check_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data[user_id]['subscription_checked'] += 1
    
    try:
        member = await bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        if member.status in ("member", "administrator", "creator"):
            pending_action = user_data[user_id]['pending_action']
            
            if pending_action == 'calculator':
                # Запускаем Mini App с калькулятором
                web_app_kb = InlineKeyboardMarkup(
                    inline_keyboard=[[
                        InlineKeyboardButton(
                            text="🚀 Открыть калькулятор", 
                            web_app=WebAppInfo(url=WEB_APP_URL)
                        )
                    ]]
                )
                await callback.message.answer(
                    "🎉 Отлично! Теперь вы можете использовать калькулятор бюджета:",
                    reply_markup=web_app_kb
                )
                
            elif pending_action == 'meditation':
                # Выдаем медитацию
                await callback.message.answer("🎉 Спасибо за подписку! Вот ваша медитация:")
                await callback.message.answer_document("CQACAgIAAxkBAAMeaBcf2YDdLQHYrvrCq_kV56zy1UUAArtwAAKY8cBIl96ssS0AAXEuNgQ")
            
            # Очищаем pending_action
            user_data[user_id]['pending_action'] = None
            
        else:
            await callback.message.answer("😔 Вы еще не подписались на канал. Пожалуйста, подпишитесь и попробуйте снова.")
            
    except TelegramBadRequest:
        await callback.message.answer("⚠️ Не удалось проверить подписку. Попробуйте позже.")

@router.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery):
    """Показ статистики через кнопку меню"""
    user_id = callback.from_user.id
    
    if user_id != ADMIN_ID:
        await callback.answer("⛔ У вас нет доступа к этой функции", show_alert=True)
        return
    
    now = datetime.datetime.now()
    active_today = sum(1 for data in user_data.values() 
                      if data['last_active'] and 
                      (now - data['last_active']).days < 1)
    
    successful_checks = sum(1 for data in user_data.values() 
                           if data['subscription_checked'] > 0)
    
    calculator_requests = sum(1 for data in user_data.values() 
                             if data['pending_action'] == 'calculator')
    meditation_requests = sum(1 for data in user_data.values() 
                             if data['pending_action'] == 'meditation')
    
    stats_text = (
        "📊 <b>Статистика бота</b>\n\n"
        f"👥 <b>Всего пользователей:</b> {bot_stats['total_users']}\n"
        f"🔔 <b>Активных за сегодня:</b> {active_today}\n"
        f"🧮 <b>Запросов калькулятора:</b> {calculator_requests}\n"
        f"🧘 <b>Запросов медитации:</b> {meditation_requests}\n"
        f"✅ <b>Проверок подписки:</b> {successful_checks}\n"
        f"🕐 <b>Последнее обновление:</b> {now.strftime('%d.%m.%Y %H:%M')}"
    )
    
    await callback.message.edit_text(stats_text, reply_markup=get_main_menu(user_id))

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Команда статистики только для админа"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас нет доступа к этой команде")
        return
    
    now = datetime.datetime.now()
    active_today = sum(1 for data in user_data.values() 
                      if data['last_active'] and 
                      (now - data['last_active']).days < 1)
    
    successful_checks = sum(1 for data in user_data.values() 
                           if data['subscription_checked'] > 0)
    
    stats_text = (
        "📊 <b>Статистика бота</b>\n\n"
        f"👥 <b>Всего пользователей:</b> {bot_stats['total_users']}\n"
        f"🔔 <b>Активных за сегодня:</b> {active_today}\n"
        f"✅ <b>Проверок подписки:</b> {successful_checks}\n"
        f"🕐 <b>Последнее обновление:</b> {now.strftime('%d.%m.%Y %H:%M')}"
    )
    
    await message.answer(stats_text)

# Остальные команды (user_stats, users) остаются без изменений
@router.message(Command("user_stats"))
async def cmd_user_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.reply_to_message:
        await message.answer("❌ Ответьте на сообщение пользователя")
        return
    
    user_id = message.reply_to_message.from_user.id
    data = user_data[user_id]
    
    user_info = (
        f"📈 <b>Статистика пользователя</b>\n\n"
        f"🆔 ID: {user_id}\n"
        f"👤 Имя: {message.reply_to_message.from_user.full_name}\n"
        f"🚀 Запусков бота: {data['start_count']}\n"
        f"✅ Проверок подписки: {data['subscription_checked']}\n"
        f"📊 Ожидаемое действие: {data['pending_action'] or 'Нет'}\n"
        f"🕐 Последняя активность: {data['last_active'].strftime('%d.%m.%Y %H:%M') if data['last_active'] else 'Никогда'}"
    )
    
    await message.answer(user_info)

@router.message(Command("users"))
async def cmd_users(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    if not user_data:
        await message.answer("📭 Еще нет пользователей")
        return
    
    users_list = "👥 <b>Пользователи бота:</b>\n\n"
    for user_id, data in list(user_data.items())[:50]:
        users_list += f"🆔 {user_id} - 🚀 {data['start_count']} раз - 📊 {data['pending_action'] or 'Нет'}\n"
    
    await message.answer(users_list)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
