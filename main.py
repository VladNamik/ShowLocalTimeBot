import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from db.db_utils import *
from telegram.handlers import register_commands
from utils import BOT_DB_SESSION_MAKER_KEY

CONFIG_FILEPATH = "./config.json"

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logging.log(logging.INFO, "Starting bot")

    # Read config, initialize bot and dispatcher
    config = Config.read_from_json(CONFIG_FILEPATH)
    bot = Bot(token=config.api_token)
    # TODO MemoryStorage is not recommended for production use, check other options
    dp = Dispatcher(bot, storage=MemoryStorage())
    register_commands(dp)

    # Initialize database
    engine = create_db_engine(config)
    bot[BOT_DB_SESSION_MAKER_KEY] = get_scoped_session(engine)

    try:
        executor.start_polling(dp, skip_updates=True)
    finally:
        dp.storage.close()
        dp.storage.wait_closed()
        bot.session.close()
