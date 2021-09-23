from pandas.core import base
import requests
import re

from lib.pmtx_client.pmtx_base import request_dql_query, request_gql



def get_root_and_children_ids(url: str, project_baseline_root_id: str) -> list:
    project_baseline_ids = []

    query = """
query getRootAndChildren($project_baseline_root_id: string) {
  root (func: uid($project_baseline_root_id)) @recurse(loop: false) {
    id: uid
    children: ProjectBaseline.children
  }
}
    """

    variables = {
        "$project_baseline_root_id": project_baseline_root_id
    }

    response = request_dql_query(url, query, variables)

    pattern = re.compile(r"'id': '.+?'")
    found_ids = pattern.findall(str(response))

    pattern = re.compile(r"'id': '(?P<id>.+)'")
    for id in found_ids:
        match = pattern.match(id)
        project_baseline_ids.append(match.group('id'))

    return project_baseline_ids



def create_baseline(url: str, baseline: dict) -> str:
    mutation = """
mutation ($baseline: AddBaselineInput!) {
  addBaseline (input: [$baseline]) {
    baseline { id }
  }
}
    """
    return request_gql(url, mutation, {"baseline": baseline})['data']['addBaseline']['baseline'][0]['id']


def copy_baseline(url: str, source_baseline_id: str):

    return



def deep_copy_project_baseline(url: str, source_project_baseline_ids: list, target_baseline_id: str) -> str:
    if target_baseline_id == '' or target_baseline_id is None: # TODO: more advanced check needed
        raise Exception("Target baseline doesn't exists, ID: ", target_baseline_id)

    query_get_pbs = """
query ($project_baseline_ids: [ID!]) {
  queryProjectBaseline (filter: {id: $project_baseline_ids}) {
    project { id }
    start
    finish
    wbs
    worktime
    parent { project {id} }
    predecessors {
      type
      project { project {id} }
    }
  }
}
    """
    variables_get_pbs = {
        "project_baseline_ids": source_project_baseline_ids
    }

    pbs = request_gql(url, query_get_pbs, variables_get_pbs)['data']['queryProjectBaseline']

    new_pbs = []
    for pb in pbs:
        new_pb = {
            "baseline": { "id": target_baseline_id },
            "project": { "id": pb['project']['id'] },
            "start": pb['start'],
            "finish": pb['finish'],
            "wbs": pb['wbs'],
            "worktime": pb['worktime'],
        }
        new_pbs.append(new_pb)



    mutate_create_pbs = """
mutation ($project_baselines: [AddProjectBaselineInput!]!) {
  addProjectBaseline (input: $project_baselines) {
    projectBaseline {
      id
      project {id}
    }
  }
}
    """
    pbs_created = request_gql(url, mutate_create_pbs, {"project_baselines": new_pbs})['data']['addProjectBaseline']['projectBaseline']
    map_pid_pbid = {}
    for i in pbs_created:
        map_pid_pbid[i['project']['id']] = i['id']



    mutate_pb_parent_predecessors = '''
mutation ($project: UpdateProjectBaselineInput!)  {
  updateProjectBaseline (input: $project) {
    numUids
  }
}
    '''
    for pb in pbs:
        if not pb['parent']:
            print("WARNING: issue doesn't have parent [issue]:", pb['project']['id'])
            continue
        if pb['project']['id'] in map_pid_pbid and pb['parent']['project']['id'] in map_pid_pbid:
            variables_update_pb = {
                "project": {
                    "filter": {"id": [map_pid_pbid[pb['project']['id']]]},
                    "set": {
                        "parent": {"id": map_pid_pbid[pb['parent']['project']['id']]},
                        # "predecessors": []
                    }
                }
            }
            # for predecessor in pb['predecessors']:
            #     if predecessor['project']['project']['id'] in map_pid_pbid:
            #         variables_update_pb['project']['set']['predecessors'].append({
            #             "type": predecessor['type'],
            #             "project": {"id": map_pid_pbid[predecessor['project']['project']['id']]}
            #         })
            #     else:
            #         ## TODO: 1. check if target baseline has this pb, if not, then create; 2. what about further dependencies?
            #         print("WARNING: Lack of project_baseline for project, ID:", predecessor['project']['project']['id'])

            # print(variables_update_pb)
            request_gql(url, mutate_pb_parent_predecessors, variables_update_pb)
        else:
            print("WARNING: issue or parent doesn't exists in map [issue, parent]:", pb['project']['id'], pb['parent']['project']['id'])

    return pbs



def create_duplicate(url: str, source_baseline_id: str, root_project_id: str, target_baseline_name: str) -> str:
    query = """
query f ($project_id: string, $baseline_id: string) { 
  project(func: type(ProjectBaseline)) 
  @filter(uid_in(ProjectBaseline.project, $project_id) {BASELINE} ) { id: uid } 
}
    """.replace("{BASELINE}", "AND uid_in(ProjectBaseline.baseline, $baseline_id)" if source_baseline_id else "AND NOT has(ProjectBaseline.baseline)")
    variables = { "$project_id": root_project_id, "$baseline_id": source_baseline_id}
    root_project_baseline_id = request_dql_query(url, query, variables)['data']['project'][0]['id']

    # if source_baseline_id is not None or source_baseline_id != "":
    #     return "Not implemented: " + str(source_baseline_id)

    pb_ids = get_root_and_children_ids(url, root_project_baseline_id)
    target_baseline_id = create_baseline(url, {
        "root": {"id": root_project_id},
        "name": target_baseline_name
    })
    deep_copy_project_baseline(url, pb_ids, target_baseline_id)

    return target_baseline_id



if __name__ == "__main__":

    url = "http://192.168.5.20:8080/"

    source_baseline_id = ""
    root_project_id = "0x4c7" # required if source_baseline_id is None


    baseline_id = create_duplicate(url, source_baseline_id, root_project_id, "some baseline")


    print("Target baseline id: ", baseline_id)

    # print(ids)
