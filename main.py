import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from db.db_utils import *
from telegram.handlers import register_commands, set_commands
from utils import BOT_DB_SESSION_MAKER_KEY

CONFIG_FILEPATH = "./config.json"


async def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logging.log(logging.INFO, "Starting bot")

    # Read config, initialize bot and dispatcher
    config = Config.read_from_json(CONFIG_FILEPATH)
    bot = Bot(token=config.api_token)
    # TODO MemoryStorage is not recommended for production use, check other options
    dp = Dispatcher(bot, storage=MemoryStorage())
    await set_commands(bot)
    register_commands(dp, config)

    # Initialize database
    engine = create_db_engine(config)
    bot[BOT_DB_SESSION_MAKER_KEY] = get_scoped_session(engine)

    # Start polling
    # TODO: add anti-flood, see https://stackoverflow.com/questions/68099134/how-to-delay-aiogram-command
    logging.log(logging.INFO, "Starting polling")
    await dp.skip_updates()
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
