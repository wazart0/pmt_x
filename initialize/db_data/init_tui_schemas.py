import requests
import sys
import os


url = sys.argv[1]

path = os.path.dirname(os.path.realpath(__file__)) + '/'

filenames = ['tui_schema.json']


query = '''
mutation {
  addPresentationSetup (input: [
    {
      tool: "tui"
      name: "Development"
      schema: put_schema_json_here
      schemaMap: "set this up properly!"
    }
  ]) {
    presentationSetup {
      id
    }
  }
}
'''


for filename in filenames:
    schema = open(path + filename, 'r').read().replace('\n', ' ').replace('"', '\\"')
    data = query.replace('put_schema_json_here', "\"" + schema + "\"")
    # print(data)
    response = requests.post(url=url, json={"query": data})

    if response.status_code != 200:
        print('Problem appeared on endpoint: ' + url)
        print(response.json())
        exit(1)
    print(response.json())