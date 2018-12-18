import requests
import traceback
from json import dumps

from config import MY_ID


class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text, keyboard=None):
        params = {'chat_id': chat_id, 'text': text, 'reply_markup': keyboard, 'parse_mode': 'Markdown'}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            return get_result[-1]
        else:
            return self.get_last_update()

    def error(self, update):
        self.send_message(MY_ID, traceback.format_exc())
        self.send_message(MY_ID, dumps(update, ensure_ascii=False))

