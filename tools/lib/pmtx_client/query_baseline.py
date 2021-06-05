import requests
import pandas as pd





def request_and_normalize_baseline_from_pmtx(url, baseline_id): # request default and some planned baseline
    query_baseline = '''
        query ($baseline_id :ID!) {
            getBaseline(id: $baseline_id) {
                projects (order: {asc: wbs}) {
                    project {id}
                    worktime
                    start
                    finish
                    parent {project {id}}
                    predecessors {type project {project {id}}}
                }
                resources {
                    project {id}
                    start
                    finish
                    resource
                }
            }
        }
    '''

    r = requests.post(url=url, json={"query": query_baseline, "variables": {"baseline_id": baseline_id}})

    if r.status_code != 200 or 'errors' in r.json():
        print('ERROR: record not ingested: ' + str(url) + '\n' + str(r.status_code) + '\n' + str(r.json()) + '\n' + str(query_baseline))
        raise Exception('problem with getting data')

    return query_baseline_normalize(r.json()['data']['getBaseline'])



def query_baseline_normalize(baseline):
    normalized_baseline = {
        "projects": [],
        "resources": []
    }

    for project in baseline['projects']:
        normalized_project = {
            "project_id": project['project']['id'],
            "worktime": project['worktime'],
            "start": project['start'],
            "finish": project['finish'],
            "parent_id": project['parent']['project']['id'] if project['parent'] else None,
            "predecessors": project['predecessors']
        }
        if project['predecessors']: # normalize predecessors
            normalized_project['predecessors'] = []
            for predecessor in project['predecessors']:
                normalized_project['predecessors'].append({
                    "type": predecessor['type'],
                    "predecessor_id": predecessor['project']['project']['id']
                })
        normalized_baseline["projects"].append(normalized_project)

    for resource in baseline['resources']:
        normalized_resource = {
            "project_id": resource['project']['id'],
            "start": resource['start'],
            "finish": resource['finish'],
            "resource_id": resource['resource']
        }
        normalized_baseline["resources"].append(normalized_resource)

    return normalized_baseline



def baseline_to_pandas_df(normalized_baseline):
    projects = normalized_baseline['projects']
    dependencies = []
    resources = normalized_baseline['resources']

    for project in projects:
        for predecessor in project['predecessors']:
            dependencies.append({
                "project_id": project['project_id'],
                "predecessor_id": predecessor['predecessor_id'],
                "type": predecessor['type']
            })
        del project['predecessors']
    
    projects_df = pd.DataFrame(projects)
    dependencies_df = pd.DataFrame(dependencies)
    resources_df = pd.DataFrame(resources) if resources else pd.DataFrame(columns={'resource_id': 'str', 'start': 'datetime64[ns]', 'finish': 'datetime64[ns]', 'project_id': 'str'})

    projects_df.worktime = pd.to_timedelta(projects_df.worktime)
    projects_df.start = pd.to_datetime(projects_df.start)
    projects_df.finish = pd.to_datetime(projects_df.finish)

    resources_df.start = pd.to_datetime(resources_df.start)
    resources_df.finish = pd.to_datetime(resources_df.finish)

    return projects_df, dependencies_df, resources_df





if __name__ == "__main__":
    # TODO: parse argv and return baseline

    url = 'http://localhost:8080/graphql'

    baseline_id = "0x2f4"
    

    normalized_baseline = request_and_normalize_baseline_from_pmtx(url, baseline_id)

    dfp, dfd, dfr = baseline_to_pandas_df(normalized_baseline)

    print(dfp)
    print(dfd)
    print(dfr)

