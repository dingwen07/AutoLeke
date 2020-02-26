import leke
import json

with open('leke_credential.json', 'r') as load_f:
    load_credential = json.load(load_f)

username = load_credential['login_name']
password = load_credential['password']
s = leke.Session(username, password)

for l in s :
    print(l.name)
