import requests

s = requests.session()
resp = s.post('https://portal.fa.ru/CoreAccount/LogOn', headers=dict(Login='185464',
                                                                            Pwd='e7afb0d5d15adb49f214bf8698b466a5'))
print(resp.text)
