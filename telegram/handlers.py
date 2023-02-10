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
from telegram.tg_utils import *
from utils import BOT_DB_SESSION_MAKER_KEY, get_datetime

COMMAND_START = "start"
COMMAND_HELP = "help"
COMMAND_TIME = "time"
COMMAND_SET_LOCATION = "set_location"
COMMAND_SET_CITY = "set_city"
COMMAND_CANCEL = "cancel"


# TODO: add schedule command to schedule meeting for specific timezone or city
# Use aioschedule or from apscheduler import AsyncIOScheduler


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
    # TODO: move commands description to commands list
    save_user_if_needed(message.bot, message.from_user)
    await state.finish()
    await message.reply("Hi! I'm ShowLocalTime bot!\nI'm new here, so please be gentle...\n"
                        "Firstly give your city or location to the bot. Then add it in a chat and just type messages")


async def show_current_time(message: types.Message, state: FSMContext):
    save_user_if_needed(message.bot, message.from_user)

    db_session_maker = message.bot.get(BOT_DB_SESSION_MAKER_KEY)
    with db_session_maker() as session:
        user = get_user_by_id(session, message.from_user.id)

    # TODO: add logging
    # logging.log(logging.INFO, "timezone is ")
    if user is not None and user.timezone is not None:
        await message.reply(datetime.now(tz=timezone(user.timezone)).strftime("%H:%M:%S"))
    else:
        await message.reply("Please share your location first: ", reply_markup=get_set_location_keyboard())
        await state.set_state(SetTimezoneStates.waiting_for_location.state)


async def show_current_group_time(message: types.Message, state: FSMContext):
    if message.chat.type != "private":
        save_user_in_group_if_needed(message.bot, tg_user=message.from_user, tg_chat=message.chat)

    db_session_maker = message.bot.get(BOT_DB_SESSION_MAKER_KEY)
    with db_session_maker() as session:
        users = get_users_for_group(session, message.chat.id)

    if users is not None and len(users) > 0:
        time_user_map = get_time_user_map(message.bot, message.from_user, message.chat, datetime.now().astimezone())
        if time_user_map is not None:
            reply_message = "\n".join(map(
                lambda user_time: make_mentions_time_str(time_user_map[user_time], user_time),
                time_user_map.keys()))

            await message.reply(reply_message, disable_notification=True)
        else:
            await message.reply("Couldn't find time string or user hasn't provided his timezone")
    else:
        # TODO: add inline keyboard
        await message.reply("Please share your location first using /set_location or /set_city commands")


async def handle_location(message: types.Message, state: FSMContext):
    save_user_if_needed(message.bot, message.from_user)

    latitude = message.location.latitude
    longitude = message.location.longitude
    tf = TimezoneFinder()
    timezone_data = timezone(tf.timezone_at(lng=longitude, lat=latitude))

    geolocator = geocoders.ArcGIS()
    location_data = geolocator.reverse([latitude, longitude])
    update_user_timezone(message.bot, message.from_user, timezone_data.zone)

    city_name = location_data.raw.get("City", "") + ", " + location_data.raw.get("CntryName", "")
    # TODO: move time format to consts or group/user settings
    current_time_str = datetime.now(tz=timezone_data).strftime("%H:%M:%S")
    reply = "Your city is {}, and your current time is {}".format(city_name, current_time_str)

    await state.finish()
    await message.answer(reply, reply_markup=types.ReplyKeyboardRemove())


async def handle_print_city_option(message: types.Message, state: FSMContext):
    await message.answer("Please write the name of your city", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(SetTimezoneStates.waiting_for_location.state)


async def handle_print_location_option(message: types.Message, state: FSMContext):
    await message.answer("Please share your location")
    await state.set_state(SetTimezoneStates.waiting_for_location.state)


async def handle_city_str(message: types.Message, state: FSMContext):
    save_user_if_needed(message.bot, message.from_user)

    geolocator = geocoders.ArcGIS()
    location = geolocator.geocode(message.text)
    if location is not None:
        tf = TimezoneFinder()
        location_data = geolocator.reverse([location.latitude, location.longitude])
        timezone_data = timezone(tf.timezone_at(lng=location.longitude, lat=location.latitude))
        logging.log(level=logging.INFO, msg=f"location address = {location_data}")

        update_user_timezone(message.bot, message.from_user, timezone_data.zone)

        city_name = location_data.raw.get("City", "") + ", " + location_data.raw.get("CntryName", "")
        current_time_str = datetime.now(tz=timezone_data).strftime("%H:%M:%S")
        reply = "Your city is {}, and your current time is {}".format(city_name, current_time_str)
        await state.finish()
        await message.answer(reply, reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("City '{}' is not recognized. Please type your city again".format(message.text))


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(f"Canceled {message.text}", reply_markup=types.ReplyKeyboardRemove())


async def handle_bot_added_to_group(message: types.ChatMemberUpdated):
    new = message.new_chat_member
    if new.status == "member":
        save_group_if_needed(message.bot, message.chat)
        await message.bot.send_message(message.chat.id, "Hi! I'm ShowLocalTimeBot, please be gentle with me, senpai...")
    elif new.status == "left":
        remove_group_if_needed(message.bot, message.chat)


async def handle_message_with_time(message: types.Message):
    if message.chat.type != "private":
        save_user_in_group_if_needed(message.bot, tg_user=message.from_user, tg_chat=message.chat)

    time_from_message = get_datetime(message.text)
    # TODO handle in different way situation when user hasn't provided his timezone
    time_user_map = get_time_user_map(message.bot, message.from_user, message.chat, time_from_message)

    if time_user_map is not None:
        reply_message = "\n".join(map(
            lambda user_time: make_mentions_time_str(time_user_map[user_time], user_time),
            time_user_map.keys()))

        await message.reply(reply_message, disable_notification=True)
    else:
        await message.reply("Couldn't find time string or user hasn't provided his timezone")


async def handle_group_messages(message: types.Message):
    save_user_in_group_if_needed(message.bot, tg_user=message.from_user, tg_chat=message.chat)


def register_commands(dp: Dispatcher, config: Config):
    # Main commands
    dp.register_message_handler(send_welcome, commands=[COMMAND_START, COMMAND_HELP], state="*")
    dp.register_message_handler(show_current_group_time, commands=COMMAND_TIME,
                                chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], state="*")
    dp.register_message_handler(show_current_time, commands=COMMAND_TIME,
                                chat_type=[types.ChatType.PRIVATE, types.ChatType.SENDER], state="*")
    dp.register_message_handler(cmd_cancel, commands=COMMAND_CANCEL, state="*")

    # Set timezone bundle
    dp.register_message_handler(handle_print_city_option, commands=COMMAND_SET_CITY, state="*")
    dp.register_message_handler(handle_print_location_option, commands=COMMAND_SET_LOCATION, state="*")
    dp.register_message_handler(handle_location, content_types=["location"],
                                state=SetTimezoneStates.waiting_for_location)
    dp.register_message_handler(handle_print_city_option, Text(equals=KEYBOARD_OPTION_PRINT_CITY, ignore_case=True),
                                state=SetTimezoneStates.waiting_for_location)
    dp.register_message_handler(handle_city_str, state=SetTimezoneStates.waiting_for_location)

    # Text filter main commands; should go after commands but before general handlers
    dp.register_message_handler(handle_message_with_time, Text(contains=config.bot_name))

    # Special cases handlers
    dp.register_my_chat_member_handler(handle_bot_added_to_group)

    # General commands and handlers
    dp.register_message_handler(handle_group_messages, chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP])

    # TODO: check register_errors_handler
