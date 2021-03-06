from json import dumps
from time import sleep

from requests import session

import config
from Bot import BotHandler
from Portal import *

DATE_KEYBOARD = dumps(
    {'keyboard': [["Сегодня", "Завтра"], ["Текущая неделя", "Следующая неделя"], ["Изменить преподавателя"]],
     'one_time_keyboard': True,
     'resize_keyboard': True})
COMMANDS = ["сегодня", "завтра", "текущая неделя", "следующая неделя", "изменить преподавателя"]
OFFSET = 0
working = {}


def auth():
    """
    Производит авторизацию на портале для дальнейших запросов
    :return: Сессия с куки
    """
    try:
        s = session()
        s.post('https://portal.fa.ru/CoreAccount/LogOn', data={'Login': config.LOGIN, 'Pwd': config.PWD})
        return s
    except Exception as e:
        print(e)
        return auth()


def start(bot, updates):
    global OFFSET
    pr = None

    if updates:
        OFFSET = updates[-1]['update_id'] + 1
        s = auth()

#    print(updates)
    for update in updates:
        try:
            user = update['message']['chat']['id']
            message = update['message']['text']

            if user not in working:
                if message == r'/start':
                    bot.send_message(user, 'Введите фамилию/ФИО преподавателя')
                    continue
                pr = find_prepod(s, message)
                if pr is None:
                    bot.send_message(user, 'Преподаватель не найден')
                    continue
                else:
                    working[user] = pr
                    bot.send_message(user, 'Выбран преподаватель: {}'.format(pr[1]),
                                     keyboard=DATE_KEYBOARD)
            elif not message.lower() in COMMANDS:
                bot.send_message(user, 'Неизвестная команда', keyboard=DATE_KEYBOARD)
            elif message.lower() == 'изменить преподавателя':
                working.pop(user)
                bot.send_message(user, 'Введите фамилию/ФИО преподавателя')
            else:
                bot.send_message(user, get_schedule(s, message, working[user]), keyboard=DATE_KEYBOARD)
        except Exception:
            bot.error(update)

#    print(working)


if __name__ == '__main__':
    print('Started')
    bot = BotHandler(config.TOKEN)
    print('Bot created')
    while 1:
        start(bot, bot.get_updates(OFFSET))
        sleep(1)
