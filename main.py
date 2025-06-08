
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

from questions import QUESTIONS, ARCHETYPES
from keep_alive import keep_alive

keep_alive()

API_TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_data = {}
logging.basicConfig(level=logging.INFO)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {"current_q": 0, "answers": []}
    await send_question(message.chat.id, user_id)

async def send_question(chat_id, user_id):
    current_q = user_data[user_id]["current_q"]
    if current_q >= len(QUESTIONS):
        await show_result(chat_id, user_id)
        return

    q = QUESTIONS[current_q]
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=option["text"])] for option in q["options"]], 
        resize_keyboard=True, 
        one_time_keyboard=True
    )
    await bot.send_message(chat_id, f"{current_q+1}. {q['text']}", reply_markup=markup)

@dp.message()
async def handle_answer(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.reply("Нажмите /start чтобы начать тест.")
        return

    current_q = user_data[user_id]["current_q"]
    q = QUESTIONS[current_q]
    selected = next((i for i, opt in enumerate(q["options"]) if opt["text"] == message.text), None)
    if selected is None:
        await message.reply("Пожалуйста, выберите один из предложенных вариантов.")
        return

    user_data[user_id]["answers"].append(q["options"][selected]["type"])
    user_data[user_id]["current_q"] += 1
    await send_question(message.chat.id, user_id)

async def show_result(chat_id, user_id):
    results = user_data[user_id]["answers"]
    score = {key: results.count(key) for key in ARCHETYPES.keys()}
    dominant = max(score, key=score.get)
    description = ARCHETYPES[dominant]

    reply = f"🔍 Ваш архетип: {dominant}\n\n{description}\n\n"
    reply += "✨ Хочешь узнать, что делать дальше? За подробной информацией или консультацией"

    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📩 Пиши сюда: @Abdulhacker")],
            [KeyboardButton(text="📲 Вступай в канал: @GuruZiWisdom")]
        ],
        resize_keyboard=True
    )

    await bot.send_message(chat_id, reply, reply_markup=markup)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
