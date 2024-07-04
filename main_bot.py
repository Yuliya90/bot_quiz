import aiosqlite
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F

# Включаем логирование
logging.basicConfig(level=logging.INFO)

API_TOKEN = '7457448495:AAERlTfSsuZzLaF5_M5BrwZ0Y1izaeDNaEc'
bot = Bot(token=API_TOKEN)
# Диспетчер
dp = Dispatcher()
# имя базы данных
DB_NAME = 'quiz_bot.db'

import quiz_quest


def generate_options_keyboard(answer_options):
    builder = InlineKeyboardBuilder()

    for index, option in enumerate(answer_options):
        # Добавляем индекс вопроса и текст кнопки в callback_data
        callback_data = f"choice_{index}"
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=callback_data)
        )

    builder.adjust(1)
    return builder.as_markup()


@dp.callback_query(F.data.startswith("choice_"))
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    idx = callback.data.split("_")[1]
    current_question_index = await func.get_quiz_index(callback.from_user.id)

    dict = quiz_quest.quiz_data[current_question_index]
    button_text = dict['options'][int(idx)]
    correct_idx = int(dict['correct_option'])
    correct_answer = dict['options'][correct_idx]
    if button_text == correct_answer :
        await callback.message.answer(f"Правильно! Вы ввели: {button_text}")
    else:
        await callback.message.answer(f"Неправильно. Вы выбрали: {button_text}. Правильный ответ: {correct_answer}")


    current_question_index += 1
    await func.update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_quest.quiz_data):
        await func.get_question(callback.message, callback.from_user.id, current_question_index)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")
    await result.save_result(callback.from_user.id, 1 if button_text == correct_answer else 0)



# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

import func


# Хэндлер на команду /quiz
@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):

    await message.answer(f"Давайте начнем квиз!")
    await func.new_quiz(message)



async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        # Сохраняем изменения
        await db.commit()



import result
@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    score = await result.get_stats(user_id)
    await message.answer(f"Ваш счет: {score}")



# Запуск процесса поллинга новых апдейтов
async def main():

    # Запускаем создание таблицы базы данных
    await create_table()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())