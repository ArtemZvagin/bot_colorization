import os
import cloudpickle
from loguru import logger
from aiogram.types import InputFile
from config import BOT_TOKEN
from aiogram import Bot, Dispatcher, executor, types

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

# Загружаем функцию которая красит изображения
with open('data/final_model.bin', 'rb') as file:
    predict = cloudpickle.load(file)['predict_func']

# Создаем файл для логирования
logger.add("data/debug.json", format="{time} {message}",
           rotation="10MB", compression="zip", serialize=True)


async def logger_info(text):
    logger.info(text)


# Сохранение черно-белых изображений
async def save_photo(path_user, message):
    full_path = f'{path_user}_{message.photo[-1].file_unique_id}.jpg'
    if not os.path.exists(full_path):
        await message.photo[-1].download(destination_file=full_path)

    return full_path


async def on_startup(_):
    print('Bot is working')


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    name = message.from_user.first_name if message.from_user.first_name else 'дорогой друг'
    text_start = f'''<b>Привет, {name}! 👋
Рад, что ты решил воспользоваться этим ботом.
Для раскраски изображения, просто отправь фото.</b>'''

    await message.answer(text_start, parse_mode='html')
    text_info = f'Пользователь {name}({message.from_user.username} ) нажал старт'
    await logger_info(text_info)


@dp.message_handler(content_types=['photo'])
async def send_photo(message: types.Message):
    await message.answer('Один момент. Обрабатываю фото...')
    user_name = message.from_user.username if message.from_user.username else 'unknown'
    first_name = message.from_user.first_name if message.from_user.first_name else 'Unknown'

    text_info = f'Пользователь {first_name}({user_name}) отправил фото'
    await logger_info(text_info)

    try:
        black_photo = await save_photo(f'data/photo_black/{user_name}', message)
        color_photo = black_photo.replace('photo_black', 'photo_color')
        predict(black_photo, color_photo)
        photo = InputFile(color_photo)
        await message.answer_photo(photo)
        await logger_info(f'{first_name}_{user_name} фото успешно отправлено!')

    except Exception as _ex:
        await message.answer('Извините произошла неизвестная ошибка!')
        await logger_info(f'{first_name}_{user_name} ошибка. {_ex}')


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
