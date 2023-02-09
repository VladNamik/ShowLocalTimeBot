import logging
from datetime import datetime

from aiogram.types import BotCommand
from timezonefinder import TimezoneFinder
from pytz import timezone
from geopy import geocoders
from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from telegram.keyboards import get_set_location_keyboard, KEYBOARD_OPTION_PRINT_CITY

COMMAND_START = "start"
COMMAND_HELP = "help"
COMMAND_TIME = "time"
COMMAND_SET_LOCATION = "set_location"
COMMAND_SET_CITY = "set_city"
COMMAND_CANCEL = "cancel"


class SetTimezoneStates(StatesGroup):
    waiting_for_location = State()


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command=f"/{COMMAND_HELP}", description="Show commands list"),
        BotCommand(command=f"/{COMMAND_TIME}", description="Get current time according to your timezone"),
        BotCommand(command=f"/{COMMAND_SET_LOCATION}", description="Set timezone using location"),
        BotCommand(command=f"/{COMMAND_SET_CITY}", description="Set timezone using city"),
        BotCommand(command=f"/{COMMAND_CANCEL}", description="Stop all questions and close keyboard")
    ]
    await bot.set_my_commands(commands)


async def send_welcome(message: types.Message, state: FSMContext):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    # TODO: move to string constants, show commands list and description
    await state.finish()
    await message.reply("Hi! I'm ShowLocalTime bot!\nI'm new here, so please be gentle...")


async def show_current_time(message: types.Message, state: FSMContext):
    # TODO:
    await message.reply("Please share your location first: ", reply_markup=get_set_location_keyboard())
    await state.set_state(SetTimezoneStates.waiting_for_location.state)


async def answer_in_group(message: types.Message, state: FSMContext):
    current_time = datetime.now().strftime("%H:%M:%S")
    logging.log(level=logging.INFO, msg=message)
    await message.answer("For groups time is : " + current_time)


async def handle_location(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lng = message.location.longitude
    tf = TimezoneFinder()
    timezone_data = timezone(tf.timezone_at(lng=lng, lat=lat))
    reply = "Your time is " + datetime.now(tz=timezone_data).strftime("%H:%M:%S")
    await message.answer(reply, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


async def handle_print_city_option(message: types.Message, state: FSMContext):
    await message.answer("Please write the name of your city", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(SetTimezoneStates.waiting_for_location.state)


async def handle_print_location_option(message: types.Message, state: FSMContext):
    await message.answer("Please share your location")
    await state.set_state(SetTimezoneStates.waiting_for_location.state)


async def handle_city_str(message: types.Message, state: FSMContext):
    geolocator = geocoders.ArcGIS()
    location = geolocator.geocode(message.text)
    if location is not None:
        tf = TimezoneFinder()
        location_data = geolocator.reverse([location.latitude, location.longitude])
        timezone_data = timezone(tf.timezone_at(lng=location.longitude, lat=location.latitude))
        logging.log(level=logging.INFO, msg=f"location address = {location_data}")
        # TODO: check this parameters
        # timezone_data.zone
        # location_data.raw.get("CntryName", "") & location_data.raw.get("City", "")
        reply = "Your time is " + datetime.now(tz=timezone_data).strftime("%H:%M:%S")
        await state.finish()
        await message.answer(reply, reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("City '{}' is not recognized. Please type your city again".format(message.text))


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Canceled", reply_markup=types.ReplyKeyboardRemove())


def register_commands(dp: Dispatcher):
    # General commands and handlers
    dp.register_message_handler(send_welcome, commands=[COMMAND_START, COMMAND_HELP])
    dp.register_message_handler(answer_in_group, chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP])

    # Main commands
    dp.register_message_handler(show_current_time, commands=COMMAND_TIME)
    dp.register_message_handler(cmd_cancel, commands=COMMAND_CANCEL)

    # Set timezone bundle
    dp.register_message_handler(handle_location, content_types=["location"],
                                state=SetTimezoneStates.waiting_for_location)
    dp.register_message_handler(handle_print_city_option, Text(equals=KEYBOARD_OPTION_PRINT_CITY, ignore_case=True),
                                state=SetTimezoneStates.waiting_for_location)
    dp.register_message_handler(handle_city_str, state=SetTimezoneStates.waiting_for_location)
    dp.register_message_handler(handle_print_city_option, commands=COMMAND_SET_CITY)
    dp.register_message_handler(handle_print_location_option, commands=COMMAND_SET_LOCATION)
