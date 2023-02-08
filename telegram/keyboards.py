from aiogram import types


def get_keyboard():
    keyboard = types.ReplyKeyboardMarkup()
    button_location = types.KeyboardButton("Share Position", request_location=True)
    button_city = types.KeyboardButton("Print location")
    keyboard.add(button_location).add(button_city)
    return keyboard
