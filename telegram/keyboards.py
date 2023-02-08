from aiogram import types


KEYBOARD_OPTION_PRINT_CITY = "Print city"
KEYBOARD_OPTION_SHARE_LOCATION = "Share location"


def get_set_location_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_location = types.KeyboardButton(KEYBOARD_OPTION_SHARE_LOCATION, request_location=True)
    button_city = types.KeyboardButton(KEYBOARD_OPTION_PRINT_CITY)
    keyboard.add(button_location).add(button_city)
    return keyboard
