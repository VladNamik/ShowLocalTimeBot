import logging
from datetime import datetime

from timezonefinder import TimezoneFinder
from pytz import timezone
from geopy import geocoders

from aiogram import Bot, Dispatcher, executor, types
from utils import *
from db_utils import *

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CONFIG_FILEPATH = "./config.json"

# Configure logging
logging.basicConfig(level=logging.INFO)

# Read config, initialize bot and dispatcher
config = Config.read_from_json(CONFIG_FILEPATH)
bot = Bot(token=config.api_token)
dp = Dispatcher(bot)
engine = create_db_engine(config)
Session = get_scoped_session(engine)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    # TODO: move to string constants
    await message.reply("Hi! I'm ShowLocalTime bot!\nI'm new here, so please be gentle...")


@dp.message_handler(commands=['time'])
async def show_current_time(message: types.Message):
    await message.reply("Please share your location first: ", reply_markup=get_keyboard())


@dp.message_handler(chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP])
async def answer_in_group(message: types.Message):
    current_time = datetime.now().strftime("%H:%M:%S")
    logging.log(level=logging.INFO, msg=message)
    await message.answer("For groups time is : " + current_time)


@dp.message_handler()
async def answer_in_private_messages(message: types.Message):
    # TODO: reply only after get city key call
    g = geocoders.ArcGIS()
    location = g.geocode(message.text)
    if location is not None:
        tf = TimezoneFinder()
        timezone_data = timezone(tf.timezone_at(lng=location.longitude, lat=location.latitude))
        logging.log(level=logging.INFO, msg=location.address)
        reply = "Your time is " + datetime.now(tz=timezone_data).strftime("%H:%M:%S")
        await message.answer(reply, reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("City '{}' is not recognized. Please type your city again".format(message.text))


def get_keyboard():
    keyboard = types.ReplyKeyboardMarkup()
    button_location = types.KeyboardButton("Share Position", request_location=True)
    button_city = types.KeyboardButton("Print location")
    keyboard.add(button_location).add(button_city)
    return keyboard


@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    lat = message.location.latitude
    lng = message.location.longitude
    tf = TimezoneFinder()
    timezone_data = timezone(tf.timezone_at(lng=lng, lat=lat))
    reply = "Your time is " + datetime.now(tz=timezone_data).strftime("%H:%M:%S")
    await message.answer(reply, reply_markup=types.ReplyKeyboardRemove())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

