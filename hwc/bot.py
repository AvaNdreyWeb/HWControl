import os

import requests
from aiogram import Bot, Dispatcher, types

SERVER = "https://hw-control-git-tg-bot-avandreyweb.vercel.app"
TOKEN = os.environ.get("TG_BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


START_MSG = (
    'Hello, I am a bot designed to '
    'track homework and class attendance.'
    '\n'
    'Please enter the code of the student you want to track.'
)


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.answer(START_MSG)


@dp.message_handler()
async def subscribe(message: types.Message):
    data = {
        'student_id': message.text,
        'chat_id': str(message.chat.id)
    }
    requests.post(f'{SERVER}/bot/subscribe', json=data)
    ok_msg = f'You successfuly subscribed on:\n<b>{message.text}</b>'
    await message.answer(ok_msg, parse_mode='HTML')


async def send_message_to_user(chat_id, message):
    await bot.send_message(int(chat_id), message)
