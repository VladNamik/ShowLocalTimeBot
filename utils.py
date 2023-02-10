import json
from dateutil import parser
from datetime import datetime
from typing import Optional

API_TOKEN_CONFIG_KEY = "api_token"
DB_FILENAME_CONFIG_KEY = "db_filename"
BOT_NAME_CONFIG_KEY = "bot_name"
BOT_DB_SESSION_MAKER_KEY = "db_session"


class Config:
    def __init__(self, token: str, db_filename: str, bot_name: str):
        self.api_token = token
        self.db_filename = db_filename
        self.bot_name = bot_name

    @classmethod
    def read_from_json(cls, filepath: str):
        with open(filepath, "r") as config_json:
            data = json.load(config_json)
            api_token = data[API_TOKEN_CONFIG_KEY]
            db_filename = data[DB_FILENAME_CONFIG_KEY]
            bot_name = data[BOT_NAME_CONFIG_KEY]

        return Config(api_token, db_filename, bot_name)


def get_datetime(string: str, fuzzy: bool = True) -> Optional[datetime]:
    """
    Returns None if string does not contain date

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        # TODO: add custom parser for other languages?
        #  Or change to custom parser cause some strings are recognized as dates when they shouldn't be
        # https://stackoverflow.com/questions/25341945/check-if-string-has-date-any-format
        return parser.parse(string, fuzzy=fuzzy)

    except ValueError:
        return None
