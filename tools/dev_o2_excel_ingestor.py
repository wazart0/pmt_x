from openpyxl import load_workbook
from openpyxl.styles import Font
from dateutil import parser
import rfc3339
from datetime import datetime
import pydgraph


from tools.lib.rdf_project_creator import RDF
from tools.lib.wbs import WBS




def str_to_rfc(datetime):
    return rfc3339.rfc3339(parser.parse(datetime))



def check_wbs_duplicates(wbs_list):
    for wbs in wbs_list:
        if wbs_list.count(wbs) > 1:
            return True
    return False



def parse_dependencies(string, separator_dependnecy = ',', separator_range = '-', separator_wbs = '.'):
    dependency_list = []
    for section in str(string).split(separator_dependnecy):
        if WBS.check(section, separator_wbs): # to check if single WBS
            dependency_list.append(WBS.normalize(section, separator_wbs))
            continue
        range = section.split(separator_range) # to check if WBS range
        if len(range) == 2 and WBS.check(range[0], separator_wbs) and WBS.check(range[1], separator_wbs):
            dependency_list = dependency_list + WBS.expand_wbs_range(WBS.normalize(range[0], separator_wbs), WBS.normalize(range[1], separator_wbs))
            continue
        # print(" !!! Not parsed dependency: '" + section + "' from '" + string + "'")
    return dependency_list



def parse_sheet_row(sheet, schema, wbs_list, idx_row):
    non_custom_columns = ['wbs', 'name', 'description', 'actual_development_time_duration', 'actual_development_time_start', 'actual_development_time_finish']

    wbs_normalized = WBS.normalize(sheet[schema['columns']['wbs'] + str(idx_row)].value)

    project = {
        "id": WBS.to_str(wbs_normalized),
        "name": sheet[schema['columns']['name'] + str(idx_row)].value.replace('\\', '/').replace('"', '\\\"'),
        # "description": str(sheet[schema['columns']['description'] + str(idx_row)].value).replace('\\', '/').replace('"', '\\\"'),
        "description": '',
        "wbs": WBS.to_str(wbs_normalized),
        "parent_id": WBS.to_str(WBS.parent(wbs_normalized))
    }

    if sheet[schema['columns']['actual_development_time_duration'] + str(idx_row)].value is not None:
        project['worktime'] = str(sheet[schema['columns']['actual_development_time_duration'] + str(idx_row)].value) + 'h'

    if sheet[schema['columns']['actual_development_time_start'] + str(idx_row)].value is not None:
        project['start'] = str_to_rfc(sheet[schema['columns']['actual_development_time_start'] + str(idx_row)].value + ' UTC')
    if sheet[schema['columns']['actual_development_time_finish'] + str(idx_row)].value is not None:
        project['finish'] = str_to_rfc(sheet[schema['columns']['actual_development_time_finish'] + str(idx_row)].value + ' UTC')

    for key in schema['columns']:
        if key not in non_custom_columns and sheet[schema['columns'][key] + str(idx_row)].value is not None:
            project[key] = sheet[schema['columns'][key] + str(idx_row)].value

    # add jira tool

    project_planned = {
        "id": project['id'],
        "wbs": project['wbs'],
        "parent_id": project['parent_id']
    }

    if sheet[schema['columns']['estimated_development_time_summary'] + str(idx_row)].value is not None:
        project_planned['worktime'] = str(sheet[schema['columns']['estimated_development_time_summary'] + str(idx_row)].value) + 'h'

    if sheet[schema['columns']['dependency'] + str(idx_row)].value is not None:
        predecessors = []
        for dependency in parse_dependencies(str(sheet[schema['columns']['dependency'] + str(idx_row)].value)):
            if dependency in wbs_list:
                predecessors.append({'id': WBS.to_str(dependency), 'type': 'FS'})
        if predecessors:
            project['predecessors'] = predecessors
            project_planned['predecessors'] = predecessors

    return project, project_planned



def generate_RDF_for_new_project(sheets, schema, wbs_list, project_name):

    rdf = RDF()

    rdf.add_root(project_name)
    rdf.add_baseline_planned('Plan at ' + datetime.now().strftime("%Y %b %d, %H:%M"))

    for sheet in sheets:
        idx_row = schema['starting_data_row']
        none_count = 0
        while none_count < 50:

            if sheet[schema['columns']['wbs'] + str(idx_row)].value is not None and WBS.check(sheet[schema['columns']['wbs'] + str(idx_row)].value) and sheet[schema['columns']['name'] + str(idx_row)].value is not None:

                project, project_planned = parse_sheet_row(sheet, schema, wbs_list, idx_row)

                rdf.add_project(**project)
                rdf.add_project_baseline_planned(**project_planned)

                none_count = 0

            else:

                if sheet[schema['columns']['wbs'] + str(idx_row)].value is not None and sheet[schema['columns']['name'] + str(idx_row)].value is not None:
                    print("ERROR: It is not WBS structure or task does not have a name: " + str(sheet[schema['columns']['wbs'] + str(idx_row)].value) + " " + str(sheet[schema['columns']['name'] + str(idx_row)].value))
                none_count = none_count + 1

            idx_row = idx_row + 1

    return rdf



def retrieve_wbs_from_sheets(sheets, schema):

    wbs_in_sheets = []

    for sheet in sheets:
        idx_row = schema['starting_data_row']
        none_count = 0
        while none_count < 50:

            if sheet[schema['columns']['wbs'] + str(idx_row)].value is not None and WBS.check(sheet[schema['columns']['wbs'] + str(idx_row)].value) and sheet[schema['columns']['name'] + str(idx_row)].value is not None:

                wbs_in_sheets.append(WBS.normalize(sheet[schema['columns']['wbs'] + str(idx_row)].value))

                none_count = 0

            else:

                if sheet[schema['columns']['wbs'] + str(idx_row)].value is not None and sheet[schema['columns']['name'] + str(idx_row)].value is not None:
                    print("ERROR: It is not WBS structure or task does not have a name: " + str(sheet[schema['columns']['wbs'] + str(idx_row)].value) + " " + str(sheet[schema['columns']['name'] + str(idx_row)].value))
                none_count = none_count + 1

            idx_row = idx_row + 1

    return wbs_in_sheets




def generate_rdf_from_xlsx(path, filename, project_name = None):

    schema = {
        "starting_data_row": 3,
        "columns": {
            "wbs": "A", # must have key, not null cell
            "name": "B", # must have key, not null cell
            "description": "C", # must have key, nullable cell
            "dependency": "D", # must have key, nullable cell
            "estimated_development_time_designer": "E",
            "estimated_development_time_reviewer": "F",
            "estimated_development_time_pm": "G",
            "estimated_development_time_summary": "H", # must have key, nullable cell
            "assigned_developer": "I",
            "actual_development_time_start": "J", # must have key, nullable cell
            "actual_development_time_finish": "K", # must have key, nullable cell
            "actual_development_time_duration": "L", # must have key, nullable cell
            "commit_statistics_insertions": "M",
            "commit_statistics_deletions": "N",
            "jira_id": "O",
            "commit_id": "P",
            "sprint": "Q",
            "comment": "R"
        }
    }

    # path = './tools/'
    workbook = load_workbook(path + filename, data_only=True)
    sheets = [workbook['Tasks']]

    wbs_list = retrieve_wbs_from_sheets(sheets, schema)

    if check_wbs_duplicates(wbs_list):
        print("ERROR: Duplicates in WBS across sheets !!!")
        return None
    if project_name is None:
        project_name = filename
    return generate_RDF_for_new_project(sheets, schema, wbs_list, project_name)



def send_rdf_to_dgraph(url, rdf):

    client_stub = pydgraph.DgraphClientStub(url)
    client = pydgraph.DgraphClient(client_stub)

    txn = client.txn()

    try:
        txn.mutate(set_nquads=str(rdf))
        txn.commit()
    except pydgraph.AbortedError:
        # Retry or handle exception.
        txn.discard()
        print(pydgraph.AbortedError)
    finally:
        txn.discard()
        print("!!! FINISHED !!!")






if __name__ == "__main__":
    # TODO: parse argv and ingest
    
    filenames = [
        # 'O2 Grouper Pipeline - Task List.xlsx',
        # 'P2 v3 Authorization_DS manager - list of tasks.xlsx',
        # 'P2 v3 Replatforming Tasks List.xlsx',
        # 'P2 testing tasks.xlsx',
    ]

    for filename in filenames:
        rdf = generate_rdf_from_xlsx('./tools/', filename)
        send_rdf_to_dgraph('localhost:9080', rdf)

