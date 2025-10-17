import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

API_TOKEN = '7900733074:AAHe06fcSukREMlysbbHnw2bHxzQv7Vyjmw'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    print("✅ Команда /start получена!")
    await message.answer("Тестовое сообщение 🎉")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
