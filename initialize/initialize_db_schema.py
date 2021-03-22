import requests
import sys
import os



url = sys.argv[1]

path = os.path.dirname(os.path.realpath(__file__)) + '/db_schema/'


schema = ''
for filename in os.listdir(path):
    schema += open(path + filename, 'r').read() + '\n'


response = requests.post(url, data=schema)


if response.status_code != 200:
    print('Problem appeared on endpoint: ' + url)
    print(response.json())
    exit(1)

print(response.json())
