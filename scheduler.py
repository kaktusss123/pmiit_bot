import requests
import datetime
from lxml import html

LOGIN_ERROR_INDICATOR = 'Для входа в систему укажите свое регистрационное имя и пароль'
UNAME = 185464
PWD = 'e7afb0d5d15adb49f214bf8698b466a5'
WEEKDAY = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']


def auth(session):
    """
    Производит авторизацию на портале
    :param session: Сессия из request
    :return: Страница с результатом для проверки успешности входа
    """
    return session.post('https://portal.fa.ru/CoreAccount/LogOn', data={'Login': UNAME,
                                                                        'Pwd': PWD})


def select_prepod(session):
    """
    Функция для поиска преподавателя по его ФИО
    :param session: Сессия
    :return: (id, name)
    """
    query = input('Введите фамилию преподавателя: ')
    resp = session.post('https://portal.fa.ru/CoreUser/SearchDialogResultAjax',
                        data={'Name': query, 'Roles': 16}).json()
    if not resp:
        print('Преподаватель не найден, попробуйте еще раз\n')
        return select_prepod(session)
    elif len(resp) > 1:
        for i, p in enumerate(resp):
            print('{}) {}'.format(i + 1, resp[i]['name']))
        num = input('Введите номер нужного преподавателя (ЗАМЕНИТЬ КЛАВИАТУРОЙ): ')
        while not num.isdigit() or not 1 <= int(num) <= len(resp):
            num = input('Попробуйте еще раз: ')
        print('Выбран преподаватель: {}'.format(resp[int(num) - 1]['name']))
        return resp[int(num) - 1]['id'], resp[int(num) - 1]['name']
    else:
        print('Выбран преподаватель: {}'.format(resp[0]['name']))
        return resp[0]['id'], resp[0]['name']


def schedule(session, prepod):
    """
    Функция выдачи расписания пользователю
    :param session: Сессия
    :param prepod: id и имя преподавателя
    :return:
    """
    while 1:
        today = (datetime.datetime.today() + datetime.timedelta(hours=3)).strftime('%d/%m/%Y')  # UTC Moscow
        command = input('ТУТ ДОЛЖНА БЫТЬ КЛАВИАТУРА\n')
        if command.lower() == 'сегодня':
            print(parse_schedule(session.post('https://portal.fa.ru/Job/SearchAjax',
                                              data={'Date': today, 'DateBegin': today, 'DateEnd': today,
                                                    'JobType': 'TUTOR',
                                                    'TutorId': prepod[0], 'Tutor': prepod[1]}).text, today,
                                 (datetime.datetime.today() + datetime.timedelta(hours=3)).weekday()))
        elif command.lower() == 'завтра':
            tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1, hours=3)).strftime('%d/%m/%Y')
            print(parse_schedule(session.post('https://portal.fa.ru/Job/SearchAjax',
                                              data={'Date': today, 'DateBegin': tomorrow, 'DateEnd': tomorrow,
                                                    'JobType': 'TUTOR',
                                                    'TutorId': prepod[0], 'Tutor': prepod[1]}).text, tomorrow,
                                 (datetime.datetime.today() + datetime.timedelta(days=1, hours=3)).weekday()))
        elif command.lower() == 'текущая неделя':
            weekday = (datetime.datetime.today() + datetime.timedelta(hours=3)).weekday()
            for delta in range(6):
                day = (datetime.datetime.today() + datetime.timedelta(days=delta - weekday, hours=3)).strftime(
                    '%d/%m/%Y')
                print(parse_schedule(session.post('https://portal.fa.ru/Job/SearchAjax',
                                                  data={'Date': today, 'DateBegin': day, 'DateEnd': day,
                                                        'JobType': 'TUTOR',
                                                        'TutorId': prepod[0], 'Tutor': prepod[1]}).text, day, delta))
        elif command.lower() == 'следующая неделя':
            for delta in range(7, 13):
                day = (datetime.datetime.today() + datetime.timedelta(days=delta, hours=3)).strftime('%d/%m/%Y')
                print(parse_schedule(session.post('https://portal.fa.ru/Job/SearchAjax',
                                                  data={'Date': today, 'DateBegin': day, 'DateEnd': day,
                                                        'JobType': 'TUTOR',
                                                        'TutorId': prepod[0], 'Tutor': prepod[1]}).text, day,
                                     delta - 7))
        elif command.lower() == 'изменить преподавателя':
            schedule(session, select_prepod(session))


def parse_schedule(table, day, w):
    """
    Функция для парсинга html таблицы в удобный для просмотра вид
    :param table: html-таблица
    :param day: datetime.strftime() объект для отображения даты
    :param w: День недели от 0 до 6
    :return: Строку, удобную для чтения
    """
    res = ''
    table = html.fromstring(table)
    disciplines = table.xpath('//tr[@class="rowDisciplines"]')
    if not disciplines:
        return '''{} - {}
        
На сегодня нет пар
'''.format(day, WEEKDAY[w])

    # date_block
    res += '{} - {}'.format(table.xpath('//tr[@class="rowDate warning"]/td[@data-field="datetime"]/text()')[0],
                            WEEKDAY[w]) + '\n\n'

    for disc in disciplines:
        # time_block
        time_block = disc.xpath('./td[@data-field="datetime"]/div/text()')
        res += '{} - {}\n'.format(*time_block[:2])
        # discipline_block
        res += disc.xpath('.//td[@data-field="discipline"]/text()')[0].strip() + '\n'
        # type_block
        res += time_block[2] + '\n' if len(time_block) > 2 else ''
        # group_block
        res += 'Группа: ' + ','.join(disc.xpath('./td[@data-field="groups"]/span/text()')).strip() + '\n'
        # where_block
        res += 'Кабинет: ' + disc.xpath('./td[@data-field="tutors"]/div/div/i/text()')[0].strip()[:-1] + \
               '\n' + disc.xpath('./td[@data-field="tutors"]/div/div/i/small/text()')[0].strip() + '\n\n\n'
    return res


if __name__ == '__main__':
    s = requests.session()

    log = auth(s)
    assert LOGIN_ERROR_INDICATOR not in log.text

    prepod = select_prepod(s)  # (id, name)

    schedule(s, prepod)
