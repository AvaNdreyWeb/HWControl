from aiogram import Dispatcher, Bot, types
import os

TOKEN = os.environ("TG_BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.answer(f"Hi, {message.from_user.full_name}")
