import json
from dateutil import parser
import rfc3339
import requests
import pandas as pd





def str_to_rfc(datetime: str) -> rfc3339.rfc3339:
    return rfc3339.rfc3339(parser.parse(datetime))


def add_child_to_parent(list: list, id: str, child: str) -> None:
    for i in list:
        if id == i['project']['id']:
            # print(i, '\n')
            if 'children' in i:
                i['children'].append(child)
            else:
                i['children'] = [child]
            return
        if 'children' in i:
            add_child_to_parent(i['children'], id, child)



def adjust_to_query_baseline(projects_df: pd.DataFrame, baseline_id: str, root_id: str) -> str:
    projects_to_parse = projects_df.copy(deep=True)

    projects_to_parse['worktime'] = projects_to_parse.worktime.apply(lambda worktime: str(float(worktime.total_seconds())/3600.) + 'h')
    projects_to_parse['start'] = projects_to_parse.start.astype(str).apply(lambda val: None if val == 'NaT' else str_to_rfc(val))
    projects_to_parse['finish'] = projects_to_parse.finish.astype(str).apply(lambda val: None if val == 'NaT' else str_to_rfc(val))

    project_baseline = [{
        "baseline": {"id": baseline_id},
        "project": {"id": root_id},
        "children": []
    }]
    children = projects_to_parse[projects_to_parse.parent_id.isnull()]
    children['parent_id'] = root_id
    while children.shape[0]:
        for child in json.loads(children.to_json(orient="records")):
            child['baseline'] = {"id": baseline_id}
            child['project'] = {"id": child['project_id']}

            parent_id = child['parent_id']
            del child['project_id']
            del child['parent_id']

            add_child_to_parent(project_baseline, parent_id, child)
        # return project_baseline
        children = projects_to_parse[projects_to_parse.parent_id.isin(children.project_id)]
    return project_baseline


def add_baseline_and_return_id(url: str, baseline_name: str, root_id: str):
    mutation_add_baseline = '''
    mutation ($baseline_name: String! $root_id: ID!) {
        addBaseline (input: [
            {
                name: $baseline_name 
                root: {id: $root_id}
            }
        ]) {
            baseline {
                id
                name
            }
        }
    }
    '''

    r = requests.post(url=url, json={
            "query": mutation_add_baseline, 
            "variables": {"baseline_name": baseline_name, "root_id": root_id}
        })

    if r.status_code != 200 or 'errors' in r.json() or r.json()['data']['addBaseline']['baseline'][0]['name'] != baseline_name:
        print('ERROR: record not ingested: ' + str(url) + '\n' + str(r.status_code) + '\n' + str(r.json()) + '\n' + str(mutation_add_baseline))
        raise Exception('problem with getting data')

    return r.json()['data']['addBaseline']['baseline'][0]['id']


def add_project_baseline(url: str, projects: pd.DataFrame, baseline_id: str, root_id: str) -> None:
    project_baseline = adjust_to_query_baseline(projects, baseline_id, root_id)

    mutation_project_baseline = '''
    mutation ($projects: [AddProjectBaselineInput!]!)  {
      addProjectBaseline (input: $projects) {
        projectBaseline {
          id
          project {
            id
          }
          baseline {
            id
          }
        }
      }
    }
    '''

    r = requests.post(url=url, json={"query": mutation_project_baseline, "variables": {"projects": project_baseline}})

    if r.status_code != 200 \
        or 'errors' in r.json() \
        or r.json()['data']['addProjectBaseline']['projectBaseline'][0]['project']['id'] != root_id \
        or r.json()['data']['addProjectBaseline']['projectBaseline'][0]['baseline']['id'] != baseline_id:

        print('ERROR: record not ingested: ' + str(url) + '\n' + str(r.status_code) + '\n' + str(r.json()) + '\n')
        raise Exception('problem with getting data')

    return




if __name__ == "__main__":
    # TODO: parse argv and ingest

    
    root_id = "0x743"
    # baseline_name = "infinite_resources_6"
    baseline_name = "limited_3"


    baseline_id = add_baseline_and_return_id(baseline_name, root_id)
    # add_project_baseline(solver.projects, baseline_id, root_id)

    print("Finished.")