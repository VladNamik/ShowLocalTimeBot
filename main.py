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


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    # TODO: move to string constants
    await message.reply("Hi! I'm ShowLocalTime bot!\nI'm new here, so please be gentle...")


@dp.message_handler(chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP])
async def echo_time_for_group(message: types.Message):
    current_time = datetime.now().strftime("%H:%M:%S")
    logging.log(level=logging.INFO, msg=message)
    await message.answer("For groups time is : " + current_time)


@dp.message_handler()
async def answer_private_messages(message: types.Message):
    # Ignore direct messages for now
    pass


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
