import requests
from pprint import pprint

s = requests.session()
r = s.post('http://portal.fa.ru/CoreAccount/LogOn', data=dict(Login='185464',
                                                               Pwd='e7afb0d5d15adb49f214bf8698b466a5'))
resp = s.post('http://portal.fa.ru/CoreUser/SearchDialogResultAjax',
              data={'Name': 'милованов', 'Roles': 16})
pprint(resp.text)
