import requests
import pandas as pd





def request_and_normalize_baselines_from_pmtx(url, query_project_filter): # request default and some planned baseline
    query_projects = '''
    query ($filter_projects: ProjectFilter!) {
        queryProject (filter: $filter_projects) {
        name
            baselines (order: {desc: name}) {
                name
                projects (order: {asc: wbs}) {
                    project {id}
                    worktime
                    start
                    finish
                    parent {project {id}}
                    predecessors {type project {project {id}}}
                }
            }
        }
    }
    '''

    r = requests.post(url=url, json={"query": query_projects, "variables": {"filter_projects": query_project_filter}})

    if r.status_code != 200 or 'errors' in r.json():
        print('ERROR: record not ingested: ' + str(url) + '\n' + str(r.status_code) + '\n' + str(r.json()) + '\n' + str(query_projects))
        raise Exception('problem with getting data')

    projects = r.json()['data']['queryProject']

    baseline_actual = query_baseline_normalize(query_baselines_merge_across_multiple_projects(projects, 0))
    baseline_planned = query_baseline_normalize(query_baselines_merge_across_multiple_projects(projects, 1))

    return baselines_merge_actual_with_planned(baseline_actual, baseline_planned)


def query_baselines_merge_across_multiple_projects(projects, baseline_number):
    baseline = []
    for project in projects:
        baseline = baseline + project['baselines'][baseline_number]['projects']
    return baseline


def query_baseline_normalize(baseline):
    normalized_baseline = []
    for project in baseline:
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
        normalized_baseline.append(normalized_project)
    return normalized_baseline


def find_project_in_baseline(project_id, baseline):
    for project in baseline:
        if project['project_id'] == project_id:
            return project
    return None


def baselines_merge_actual_with_planned(baseline_actual, baseline_planned):
    baseline = baseline_actual
    for project in baseline:
        if project['worktime'] is None:
            project['worktime'] = find_project_in_baseline(project['project_id'], baseline_planned)['worktime']
            if project['worktime'] is None: 
                # print("Missing worktime for project")
                project['worktime'] = '0h'
        if project['finish'] is None:
            project['start'] = None
    return baseline


def baseline_to_pandas_df(normalized_baseline):
    projects = normalized_baseline
    dependencies = []
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

    projects_df.worktime = pd.to_timedelta(projects_df.worktime)
    projects_df.start = pd.to_datetime(projects_df.start)
    projects_df.finish = pd.to_datetime(projects_df.finish)

    return projects_df, dependencies_df





if __name__ == "__main__":
    # TODO: parse argv and return baseline

    url = 'http://localhost:8080/graphql'


    query_project_filter = {
        "name": {"allofterms": "P2 v3 Replatforming Tasks List.xlsx"}, 
        "or": {
            "name": {"allofterms": "O2 Grouper Pipeline - Task List.xlsx"}, 
            "or": {
                "name": {"allofterms": "P2 v3 Authorization_DS manager - list of tasks.xlsx"}
            }
        }
    }


    normalized_baseline = request_and_normalize_baselines_from_pmtx(url, query_project_filter)

    print(normalized_baseline)

