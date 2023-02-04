import json

API_TOKEN_CONFIG_KEY = "api_token"


class Config:
    def __init__(self, token: str):
        self.api_token = token

    @classmethod
    def read_from_json(cls, filepath: str):
        api_token = None
        with open(filepath, "r") as config_json:
            data = json.load(config_json)
            api_token = data[API_TOKEN_CONFIG_KEY]

        return Config(api_token)
