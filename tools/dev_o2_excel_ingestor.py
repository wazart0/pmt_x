from openpyxl import load_workbook
from openpyxl.styles import Font
import requests
import pydgraph


def get_schema_from_sheet(sheet): # TODO schema validation
    schema = {}
    schema['offset_row'] = 1 # offset of WBS: TODO search for WBS
    schema['offset_col'] = 0 # offset of WBS: TODO search for WBS
    # schema['header_1'] = [i.value for i in sheet['1']] # TODO apply offsets
    # schema['header_2'] = [i.value for i in sheet['2']] # TODO apply offsets
    # schema['map_to_jira'] = { # TODO something with history (start, finish, duration columns)
    #     'Name': 'summary',
    #     'Description': 'description',
    #     'Jira ID': 'key',
    # }
    schema['columns'] = { # TODO make it dynamic
        'WBS': 'A',
        'Name': 'B',
        'Description': 'C',
        'Jira ID': 'R',
    }
    schema['data_offset_row'] = 3
    return schema

    
def excel_to_json(map, schema, sheet):
    tasks_to_json = []
    i = schema['data_offset_row']
    while sheet[schema['columns']['WBS'] + str(i)].value is not None:
        if len(str(sheet[schema['columns']['Name'] + str(i)].value)) != 0:
            task = {}
            for column in map:
                task[map[column]] = str(sheet[column + str(i)].value)
            tasks_to_json.append(task)
        i = i + 1
    return tasks_to_json



url = 'http://localhost:8080/graphql'

# filename = 'grouper.xlsx'
# label = 'P2_pipelines'

filename = 'p2v3.xlsx'
label = 'P2_v3'

# filename = 'auth.xlsx'
# label = 'Authorization'



# workbook = load_workbook(filename=filename)
# sheet = workbook['Tasks']

# schema = get_schema_from_sheet(sheet)


map = {
    "A": "wbs",
    "B": "name",
    "C": "description",
    "D": "dependency",
    "E": "estimated_development_time_designer",
    "F": "estimated_development_time_reviewer",
    "G": "estimated_development_time_pm",
    "H": "assigned_developer",
    "I": "estimated_testing_time_tester",
    "J": "estimated_testing_time_pm",
    "K": "assigned_tester",
    "L": "actual_development_time_start",
    "M": "actual_development_time_finish",
    "N": "actual_development_time_duration",
    "O": "commit_statistics_insertions",
    "P": "commit_statistics_deletions",
    "Q": "code_documentation_time",
    "R": "jira_id",
    "S": "commit_id",
    "T": "sprint",
    "U": "comment"
}


# tasks_json = excel_to_json(map, schema, sheet)


query_add_root_project = '''
mutation {
  addProject(input: [
    {
      name: "project_name"
      description: "project_description"
    }
  ]) {
    project{
      id
    }
  }
}
'''

data = query_add_root_project
response = requests.post(url=url, json={"query": data})

if response.status_code != 200:
    print('Problem appeared on endpoint: ' + url)
    print(response.json())
    exit(1)
print(response.json()['data']['addProject']['project'][0]['id'])



