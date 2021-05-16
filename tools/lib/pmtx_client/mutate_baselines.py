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



def adjust_to_query_project_baseline(projects: pd.DataFrame, baseline_id: str, root_id: str) -> str:
    project_baseline = [{
        "baseline": {"id": baseline_id},
        "project": {"id": root_id},
        "start": str_to_rfc(str(projects[projects.start.notnull()].start.min())),
        "finish": str_to_rfc(str(projects[projects.finish.notnull()].finish.max())),
        "worktime": str(float(projects[projects.worktime.notnull()].worktime.sum().total_seconds())/3600.) + 'h',
        "children": []
    }]

    projects_to_parse = projects[projects.project_id != root_id].copy(deep=True)
    projects_to_parse.loc[projects_to_parse.parent_id == root_id, 'parent_id'] = None

    projects_to_parse['worktime'] = projects_to_parse.worktime.apply(lambda val: str(float(val.total_seconds())/3600.) + 'h')
    projects_to_parse['start'] = projects_to_parse.start.astype(str).apply(lambda val: None if val == 'NaT' else str_to_rfc(val))
    projects_to_parse['finish'] = projects_to_parse.finish.astype(str).apply(lambda val: None if val == 'NaT' else str_to_rfc(val))

    children = projects_to_parse[projects_to_parse.parent_id.isnull()]
    children.loc['parent_id'] = root_id
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
    project_baseline = adjust_to_query_project_baseline(projects, baseline_id, root_id)

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

    print(r.json())

    if r.status_code != 200 \
        or 'errors' in r.json() \
        or r.json()['data']['addProjectBaseline']['projectBaseline'][0]['project']['id'] != root_id \
        or r.json()['data']['addProjectBaseline']['projectBaseline'][0]['baseline']['id'] != baseline_id:

        print('ERROR: record not ingested: ' + str(url) + '\n' + str(r.status_code) + '\n' + str(r.json()) + '\n')
        raise Exception('problem with getting data')

    return


def adjust_to_query_resource_baseline(resources: pd.DataFrame, baseline_id: str) -> str:
    resource_to_parse = resources[resources.project_id.notnull()].copy(deep=True)

    resource_to_parse['worktime'] = resource_to_parse.finish - resource_to_parse.start

    resource_to_parse['worktime'] = resource_to_parse.worktime.apply(lambda val: str(float(val.total_seconds())/3600.) + 'h')
    resource_to_parse['start'] = resource_to_parse.start.astype(str).apply(lambda val: None if val == 'NaT' else str_to_rfc(val))
    resource_to_parse['finish'] = resource_to_parse.finish.astype(str).apply(lambda val: None if val == 'NaT' else str_to_rfc(val))

    resource_to_parse.rename(inplace=True, columns={"resource_id": "resource"})

    resource_to_parse = resource_to_parse.to_dict(orient="records")

    for resource in resource_to_parse:
        resource['baseline'] = {"id": baseline_id}
        resource['project'] = {"id": resource['project_id']}
        del resource['project_id']

    return resource_to_parse


def add_resource_baseline(url: str, resources: pd.DataFrame, baseline_id: str) -> None:
    resource_baseline = adjust_to_query_resource_baseline(resources, baseline_id)

    mutation_project_baseline = '''
    mutation ($resources: [AddResourceBaselineInput!]!)  {
      addResourceBaseline (input: $resources) {
        numUids
      }
    }
    '''

    r = requests.post(url=url, json={"query": mutation_project_baseline, "variables": {"resources": resource_baseline}})

    if r.status_code != 200 \
        or 'errors' in r.json() \
        or r.json()['data']['addResourceBaseline']['numUids'] != resources[resources.project_id.notnull()].shape[0]:

        print('ERROR: record not ingested: ' + str(url) + '\n' + str(r.status_code) + '\n' + str(r.json()) + '\n')
        raise Exception('problem with getting data')

    return


def modify_project_baseline_predecessors(url: str, dependencies_df: pd.DataFrame, baseline_id: str):
    dependencies = dependencies_df.copy(deep=True)

    query_projectbaseline = '''
        query ($baseline_id:ID!) {
            getBaseline (id: $baseline_id) {
                projects {
                    id
                    project {id}
                }
            }
        }
    '''

    r = requests.post(url=url, json={"query": query_projectbaseline, "variables": {"baseline_id": baseline_id}})

    if r.status_code != 200 or 'errors' in r.json():
        print('ERROR: record not ingested: ' + str(url) + '\n' + str(r.status_code) + '\n' + str(r.json()) + '\n' + str(query_projectbaseline))
        raise Exception('problem with getting data')

    projects_mask = []

    for project in r.json()['data']['getBaseline']['projects']:
        projects_mask.append({
            "project_id": project['project']['id'],
            "project_baseline_id": project['id']
        })

    dependencies = dependencies.merge(pd.DataFrame(projects_mask), how='left', on='project_id')
    dependencies = dependencies.merge(pd.DataFrame(projects_mask), how='left', left_on='predecessor_id', right_on='project_id')
    dependencies.drop(inplace=True, columns=['project_id_x', 'project_id_y', 'predecessor_id'])
    dependencies.rename(inplace=True, columns={'project_baseline_id_x': 'project_baseline_id', 'project_baseline_id_y': 'predecessor_baseline_id'})


    variables = []

    for _, row in dependencies.iterrows():
        var = None
        for i in variables:
            var = i if i['project']['filter']['id'][0] == row['project_baseline_id'] else None
        if var:
            var['project']['set']['predecessors'].append({"type": row['type'], "project": {"id": row['predecessor_baseline_id']}})
        else:
            variables.append({
                "project": {
                    "filter": {
                        "id": [
                            row['project_baseline_id']
                        ]
                    },
                    "set": {
                        "predecessors": [
                            {
                                "type": row['type'],
                                "project": {
                                    "id": row['predecessor_baseline_id']
                                }
                            }
                        ]
                    }
                }
            })

    mutation_projectbaseline_predecessors = '''
        mutation ($project: UpdateProjectBaselineInput!)  {
            updateProjectBaseline (input: $project) {
                numUids
            }
        }
    '''

    for i in variables:
        r = requests.post(url=url, json={"query": mutation_projectbaseline_predecessors, "variables": i})

        if r.status_code != 200 or 'errors' in r.json():
            print('ERROR: record not ingested: ' + str(url) + '\n' + str(r.status_code) + '\n' + str(r.json()) + '\n' + str(query_projectbaseline))
            raise Exception('problem with getting data')






if __name__ == "__main__":
    # TODO: parse argv and ingest

    
    root_id = "0x743"
    # baseline_name = "infinite_resources_6"
    baseline_name = "limited_3"


    baseline_id = add_baseline_and_return_id(baseline_name, root_id)
    # add_project_baseline(solver.projects, baseline_id, root_id)
    # add_resource_baseline(url, solver.av, baseline_id)

    print("Finished.")