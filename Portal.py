import datetime

from lxml import html

WEEKDAY = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']


def find_prepod(session, name):
    resp = session.post('http://portal.fa.ru/CoreUser/SearchDialogResultAjax',
                        data={'Name': name, 'Roles': 16})
    resp = resp.json()
    if not resp:
        return None
    else:
        return resp[0]['id'], resp[0]['name']


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
        return '\n{} [{}]\nНет пар\n'.format(day, WEEKDAY[w])

    # date_block
    res += '\n{}'.format(table.xpath('//tr[@class="rowDate warning"]/td[@data-field="datetime"]/text()')[0]) + '\n\n'

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
               '\n' + disc.xpath('./td[@data-field="tutors"]/div/div/i/small/text()')[0].strip() + '\n\n'
    return res


def get_schedule(session, command, prepod):
    today = (datetime.datetime.today() + datetime.timedelta(hours=3)).strftime('%d/%m/%Y')
    if prepod is None:
        return
    if command.lower() == 'сегодня':
        return parse_schedule(session.post('http://portal.fa.ru/Job/SearchAjax',
                                           data={'Date': today, 'DateBegin': today, 'DateEnd': today,
                                                 'JobType': 'TUTOR',
                                                 'TutorId': prepod[0], 'Tutor': prepod[1]}).text, today,
                              (datetime.datetime.today() + datetime.timedelta(hours=3)).weekday())
    elif command.lower() == 'завтра':
        tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1, hours=3)).strftime('%d/%m/%Y')
        return (parse_schedule(session.post('http://portal.fa.ru/Job/SearchAjax',
                                            data={'Date': today, 'DateBegin': tomorrow, 'DateEnd': tomorrow,
                                                  'JobType': 'TUTOR',
                                                  'TutorId': prepod[0], 'Tutor': prepod[1]}).text, tomorrow,
                               (datetime.datetime.today() + datetime.timedelta(days=1, hours=3)).weekday()))
    elif command.lower() == 'текущая неделя':
        weekday = (datetime.datetime.today() + datetime.timedelta(hours=3)).weekday()
        res = ''
        for delta in range(6):
            day = (datetime.datetime.today() + datetime.timedelta(days=delta - weekday, hours=3)).strftime(
                '%d/%m/%Y')
            res += (parse_schedule(session.post('http://portal.fa.ru/Job/SearchAjax',
                                                data={'Date': today, 'DateBegin': day, 'DateEnd': day,
                                                      'JobType': 'TUTOR',
                                                      'TutorId': prepod[0], 'Tutor': prepod[1]}).text, day, delta))
        return res
    elif command.lower() == 'следующая неделя':
        weekday = (datetime.datetime.today() + datetime.timedelta(hours=3)).weekday()
        res = ''
        for delta in range(7, 13):
            day = (datetime.datetime.today() + datetime.timedelta(days=delta - weekday, hours=3)).strftime('%d/%m/%Y')
            res += (parse_schedule(session.post('http://portal.fa.ru/Job/SearchAjax',
                                                data={'Date': today, 'DateBegin': day, 'DateEnd': day,
                                                      'JobType': 'TUTOR',
                                                      'TutorId': prepod[0], 'Tutor': prepod[1]}).text, day,
                                   delta - 7))
        return res
