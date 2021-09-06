import requests
import sys
import os
import time



url = sys.argv[1]

path = os.path.dirname(os.path.realpath(__file__)) + '/db_schema/'


schema = ''
for filename in os.listdir(path):
    schema += open(path + filename, 'r').read() + '\n'


response = requests.post(url, data=schema)

while True:
    if response.status_code == 200 and 'errors' in response.json():
        print('Problem appeared on endpoint: ' + url)
        print(response.json()['errors'])
        print('Retrying connection in 10s ...')
        time.sleep(10)
        response = requests.post(url, data=schema)
    elif response.status_code != 200 or 'errors' in response.json():
        print('Problem appeared on endpoint: ' + url)
        print(response.text)
        exit(1)
    else:
        break
    

print(response.json())
