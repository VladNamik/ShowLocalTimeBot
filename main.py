import logging

from aiogram import Bot, Dispatcher, executor
from db.db_utils import *
from telegram.handlers import register_commands

CONFIG_FILEPATH = "./config.json"

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Read config, initialize bot and dispatcher
    config = Config.read_from_json(CONFIG_FILEPATH)
    bot = Bot(token=config.api_token)
    dp = Dispatcher(bot)
    register_commands(dp)

    # Initialize database
    engine = create_db_engine(config)
    Session = get_scoped_session(engine)

    executor.start_polling(dp, skip_updates=True)
