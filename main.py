import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, executor, types
from utils import Config

CONFIG_FILEPATH = "./config.json"

# Configure logging
logging.basicConfig(level=logging.INFO)

# Read config, initialize bot and dispatcher
config = Config.read_from_json(CONFIG_FILEPATH)
bot = Bot(token=config.api_token)
dp = Dispatcher(bot)


@dp.message_handler()
async def echo(message: types.Message):
    current_time = datetime.now().strftime("%H:%M:%S")
    logging.log(level=logging.INFO, msg=message)
    await message.answer(message.text + "; " + current_time)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
