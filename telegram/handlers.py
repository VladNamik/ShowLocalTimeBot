import logging
from datetime import datetime
from timezonefinder import TimezoneFinder
from pytz import timezone
from geopy import geocoders
from aiogram import Dispatcher, types

from telegram.keyboards import get_keyboard


async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    # TODO: move to string constants
    await message.reply("Hi! I'm ShowLocalTime bot!\nI'm new here, so please be gentle...")


async def show_current_time(message: types.Message):
    await message.reply("Please share your location first: ", reply_markup=get_keyboard())


async def answer_in_group(message: types.Message):
    current_time = datetime.now().strftime("%H:%M:%S")
    logging.log(level=logging.INFO, msg=message)
    await message.answer("For groups time is : " + current_time)


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


async def handle_location(message: types.Message):
    lat = message.location.latitude
    lng = message.location.longitude
    tf = TimezoneFinder()
    timezone_data = timezone(tf.timezone_at(lng=lng, lat=lat))
    reply = "Your time is " + datetime.now(tz=timezone_data).strftime("%H:%M:%S")
    await message.answer(reply, reply_markup=types.ReplyKeyboardRemove())


def register_commands(dp: Dispatcher):
    dp.register_message_handler(handle_location, commands="location")
    dp.register_message_handler(send_welcome, commands=["start", "help"])
    dp.register_message_handler(show_current_time, commands="time")
    dp.register_message_handler(answer_in_group, chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP])
    dp.register_message_handler(answer_in_private_messages)
