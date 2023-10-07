# %%
import requests
import pickle
import json
import rfc3339
import pandas as pd

import lib.jira.jira as jira
from lib.pmtx_client import query_baseline
from lib.pmtx_client.pmtx_base import request_dql_mutate, request_gql, request_dql_query

from lib.task_assignee_estimators.solver_base import SolverBase






def create_project_pb_externaltool(url: str, name: str, original_baseline_id: str, description = None, external_tool = {}, if_root = False) -> dict:

    serialized_description = '_:project <Project.description> {0} .'.format(json.dumps(description)) if description else ""

    baseline_original = ""
    if if_root:
        original_baseline_id = "_:baseline_original"
        baseline_original = """
    _:baseline_original <Baseline.root> _:project .
    _:baseline_original <Baseline.projects> _:project_baseline_original .
    _:baseline_original <Baseline.name> "Jira Original" .
    _:project <Project.baselines> _:baseline_original .
    _:baseline_original <dgraph.type> "Baseline" .
        """

    create_project = '''
{
  set {
    _:project <dgraph.type> "Project" .
    _:project <Project.name> {name} .
    {project_description}
    
    _:project <Project.projectBaselines> _:project_baseline .
    _:project_baseline <dgraph.type> "ProjectBaseline" .
    _:project_baseline <ProjectBaseline.project> _:project .
    
    _:project <Project.projectBaselines> _:project_baseline_original .
    _:project_baseline_original <dgraph.type> "ProjectBaseline" .
    _:project_baseline_original <ProjectBaseline.project> _:project .
    _:project_baseline_original <ProjectBaseline.baseline> <{original_baseline_id}> .

    {ExternalTool}
    {BaselineOriginal}
  }
}
    '''. \
        replace("{name}", json.dumps(name)). \
        replace("{project_description}", serialized_description). \
        replace("{original_baseline_id}", original_baseline_id). \
        replace("{BaselineOriginal}", baseline_original)


    exttool = ""
    if external_tool:
        exttool = """
    _:project <Project.externalTool> _:exttool .
    _:exttool <dgraph.type> "ExternalTool" .
    _:exttool <ExternalTool.project> _:project .
    _:exttool <ExternalTool.externalID> "{externalID}" .
    _:exttool <ExternalTool.name> "{name}" .
    _:exttool <ExternalTool.type> "{type}" .
    _:exttool <ExternalTool.url> "{url}" .
    _:exttool <ExternalTool.urlSubpath> "{urlSubpath}" .
        """.format(**external_tool) # replace("{externalID}", external_tool['externalID']). \
        #     replace("{name}", external_tool['name']). \
        #     replace("{type}", external_tool['type']). \
        #     replace("{url}", external_tool['url']). \
        #     replace("{urlSubpath}", external_tool['urlSubpath'])
    
    if 'customFields' in external_tool:
        exttool = exttool + """_:exttool <ExternalTool.customFields> {0} .""".format(json.dumps(external_tool['customFields']))
        
    create_project = create_project.replace("{ExternalTool}", exttool)

    # print(create_project)
    response = request_dql_mutate(url, create_project)
    # print(response)

    return response['data']['uids']





# def sync_baseline_from_jira(baseline_id: str, url: str, jira_info: dict) -> None:

#     query = """
#         query ($baseline_id :ID!) {
#             getBaseline(id: $baseline_id) {
#                 projects {
#                     id
#                     project {customFields}
#                 }
#             }
#         }
#     """

#     query_variables = {"baseline_id": baseline_id}


#     r = requests.post(url=url, json={"query": query, "variables": query_variables})
#     if r.status_code != 200 or "errors" in r.json():
#         print("ERROR: record not ingested: " + str(url) + "\n" + str(r.status_code) + "\n" + str(r.json()) + "\n" + str(query))
#         raise Exception("problem with getting data")


#     mutation = """
#         mutation ($project_baseline_id: ID!, $fields: ProjectBaselinePatch!) {
#             updateProjectBaseline (input: {filter: {id: [$project_baseline_id]} set: $fields}) {
#                 numUids
#             }
#         }
#     """

#     for project in r.json()["data"]["getBaseline"]["projects"]:
#         if project["project"]["customFields"]:
#             custom_fields = json.loads(project["project"]["customFields"])
#             if "jira_id" in custom_fields:
#                 issue_changelog = jira.get_issue_and_changelog(jira_info, custom_fields["jira_id"])
#                 start = jira.get_issue_first_transition_date(issue_changelog, "In Development")
#                 start = rfc3339.rfc3339(start) if start else None
#                 finish = jira.get_issue_last_transition_date(issue_changelog, "Code Complete")
#                 finish = rfc3339.rfc3339(finish) if finish else None
#                 print(project["id"], custom_fields["jira_id"], start, finish)

#                 if start or finish:
#                     variables = {
#                         "project_baseline_id": project["id"],
#                         "fields": {
#                             "start": start,
#                             "finish": finish
#                         }
#                     }
#                     r = requests.post(url=url, json={"query": mutation, "variables": variables})
#                     if r.status_code != 200 or "errors" in r.json():
#                         print("ERROR: record not ingested: " + str(url) + "\n" + str(r.status_code) + "\n" + str(r.json()) + "\n" + str(mutation))
#                         raise Exception("problem with getting data")

#     print("Finished.")






def sync_issues_and_projects_by_jql(url: str, jira_info: dict, jql: str, original_baseline_id: str):

    issues = jira.get_issues(jira_info, jql)
    parsed_issues = []
    for issue in issues:
        parsed = {
            "name": issue["fields"]["summary"],
            "description": issue["fields"]["description"],
            "externalTool": [{
                "externalID": issue["key"],
                "name": jira_info["name"],
                "type": "Jira",
                "url": jira_info["url"],
                "urlSubpath": "browse/" + issue["key"],
                "customFields": json.dumps({
                    "component": ",".join([i["name"] for i in issue["fields"]["components"]]),
                    "type": issue["fields"]["issuetype"]["name"],
                    "status": issue["fields"]["status"]["name"],
                    "statusCategory": issue["fields"]["status"]["statusCategory"]["name"],
                    "bugOrigin": issue["fields"]["customfield_11748"]["value"] if issue["fields"]["customfield_11748"] is not None else None,
                })
            }]
        }

        parsed_issues.append(parsed)

    get_already_existing_issues = '''
query ($jiraIDs: [String!]! $url: String!) {
  queryExternalTool (filter: {and: [{externalID: {in: $jiraIDs}} {url: {eq: $url}}]}) {
    externalID
    project {id}
  }
}
    '''

    response = request_gql(url, get_already_existing_issues, {"jiraIDs": [i['externalTool'][0]['externalID'] for i in parsed_issues], "url": jira_info['url']})

    map_jira_pmt = {}
    for i in response['data']['queryExternalTool']:
        map_jira_pmt[i['externalID']] = i['project']['id']

    update_project = '''
mutation ($id: ID! $projectFields: ProjectPatch! $jiraID: String! $url: String! $externalToolFields: ExternalToolPatch) {
  updateProject (input: {
      filter: { id: [$id] }
      set: $projectFields
    }) {
      numUids
    }
  updateExternalTool (input: {
      filter: {and: [{externalID: {eq: $jiraID}} {url: {eq: $url}}]}
      set: $externalToolFields
    }) {
      numUids
    }
}
    '''

    projects_to_create = []    
    for issue in parsed_issues:
        if issue['externalTool'][0]['externalID'] in map_jira_pmt:
            response = request_gql(url, update_project, 
                {
                    "id": map_jira_pmt[issue['externalTool'][0]['externalID']],
                    "projectFields": {i: issue[i] for i in issue if i != 'externalTool'},
                    "jiraID": issue['externalTool'][0]['externalID'],
                    "url": jira_info["url"],
                    "externalToolFields": {i: issue['externalTool'][0][i] for i in issue['externalTool'][0] if i != 'externalID'}
                }
            )
        else:
            projects_to_create.append(issue)


    for issue in projects_to_create:
        # print(issue['externalTool'][0]['externalID'])
        create_project_pb_externaltool(url, issue['name'], original_baseline_id, issue['description'], issue['externalTool'][0])

    return issues






def sync_default_and_original_baseline(url: str, jira_info: dict, issues: dict, root_project_baseline_id: str, baseline_original_id: str, project_baseline_original_id: str): 

    query = """
query v ($baseline_id: string) {
  pbs  (func: type(ExternalTool)) @filter(eq(ExternalTool.externalID, {jira_ids})) @normalize {
    externalID: ExternalTool.externalID
    act: ExternalTool.project {
      Project.projectBaselines @filter(not has(ProjectBaseline.baseline)) {
        actual_id: uid
      	}
      }
    ori: ExternalTool.project {
      Project.projectBaselines @filter(uid_in(ProjectBaseline.baseline, $baseline_id)) {
        original_id: uid
      }
    }
  }
}
    """.replace("{jira_ids}", json.dumps([issue['key'] for issue in issues]))
    response = request_dql_query(url, query, {"$baseline_id": baseline_original_id})

    map_jira_pmt = {}
    for i in response['data']['pbs']:
        map_jira_pmt[i['externalID']] = {
            'actual_id': i['actual_id'],
            'original_id': i['original_id'],
        }



    mutation = """
mutation ($project_baseline_id: ID!, $fields: ProjectBaselinePatch!) {
  updateProjectBaseline (input: {filter: {id: [$project_baseline_id]} set: $fields}) {
    numUids
  }
}
    """

    for issue in issues:
        if issue['key'] in map_jira_pmt:
            issueCL = jira.get_issue_changelog(jira_info, issue['key'])
            pb = {}
            pb_original = {}

            if issue['fields']['issuetype']['name'] == "Sub-task":
                if issue['fields']['parent']['key'] in map_jira_pmt:
                    pb['parent'] = {"id": map_jira_pmt[issue['fields']['parent']['key']]['actual_id']}
                    pb_original['parent'] = {"id": map_jira_pmt[issue['fields']['parent']['key']]['original_id']}
                else:
                    print("WARNING: parent not in map [current, parent]:", issue['key'], '->', issue['fields']['parent']['key'])


            for link in issue['fields']['issuelinks']:
                if link['type']['inward'] == 'split from' and 'inwardIssue' in link:
                    if link['inwardIssue']['key'] in map_jira_pmt:
                        pb['parent'] = {"id": map_jira_pmt[link['inwardIssue']['key']]['actual_id']}
                        pb_original['parent'] = {"id": map_jira_pmt[link['inwardIssue']['key']]['original_id']}
                    else:
                        print("WARNING: parent not in map [current, parent]:", issue['key'], '->', link['inwardIssue']['key'])
                if link['type']['inward'] == 'has to be done after' and 'inwardIssue' in link:
                    if link['inwardIssue']['key'] in map_jira_pmt:
                        if 'predecessors' not in pb: pb['predecessors'] = []
                        pb['predecessors'].append({
                            "type": "FS",
                            "project": {"id": map_jira_pmt[link['inwardIssue']['key']]['actual_id']}
                            })

                        if 'predecessors' not in pb_original: pb_original['predecessors'] = []
                        pb_original['predecessors'].append({
                            "type": "FS",
                            "project": {"id": map_jira_pmt[link['inwardIssue']['key']]['original_id']}
                            })
                    else:
                        print("WARNING: predecessor not in map [current, predecessor]:", issue['key'], '->', link['inwardIssue']['key'])


            if issue['fields']['timeoriginalestimate']:
                pb_original['worktime'] = str(issue['fields']['timeoriginalestimate']/3600.) + 'h'

            if issue['fields']['customfield_11737'] or issue['fields']['timespent']: #custom solution (for older projects)
                if issue['fields']['customfield_11737'] and issue['fields']['timespent']:
                    pb['worktime'] = issue['fields']['customfield_11737'] if issue['fields']['customfield_11737'] > issue['fields']['timespent'] else issue['fields']['timespent']
                elif issue['fields']['timespent']:
                    pb['worktime'] = issue['fields']['timespent']
                elif issue['fields']['customfield_11737']:
                    pb['worktime'] = issue['fields']['customfield_11737']
                if 'worktime' in pb:
                    pb['worktime'] = str(pb['worktime']/3600.) + 'h'

            start = jira.get_issue_first_transition_date(issueCL, ["In Development", "In Progress"])
            finish = jira.get_issue_last_transition_date(issueCL, ["Closed"])
            if start: pb['start'] = rfc3339.rfc3339(start)
            if finish: pb['finish'] = rfc3339.rfc3339(finish)

            if root_project_baseline_id is not None and 'parent' not in pb:
                pb['parent'] = {"id": root_project_baseline_id}
            if project_baseline_original_id is not None and 'parent' not in pb_original:
                pb_original['parent'] = {"id": project_baseline_original_id}

            if pb:
                request_gql(url, mutation, {
                    "project_baseline_id": map_jira_pmt[issue['key']]['actual_id'],
                    "fields": pb
                })

            if pb_original:
                request_gql(url, mutation, {
                    "project_baseline_id": map_jira_pmt[issue['key']]['original_id'],
                    "fields": pb_original
                })

    return






def import_project_from_jira(url: str, jira_info: dict, project: str) -> str:
    externalTool = request_gql(url, """
query ($jiraIDs: [String!]! $url: String!) {
  queryExternalTool (filter: {and: [{externalID: {in: $jiraIDs}} {url: {eq: $url}}]}) {
    project { 
      id
      projectBaselines (filter: { not: {has: baseline} }) { id }
      baselines (filter: {name: {allofterms: "Jira Original"}}) {
        id
      }
    }
  }
}
    """, {"jiraIDs": [project], "url": jira_info['url']})['data']['queryExternalTool']


    if len(externalTool) > 1:
        raise Exception("ERROR: duplicated ID in the system: ", externalTool)


    if not externalTool:
        ids = create_project_pb_externaltool(
            url=url, 
            name=project, 
            original_baseline_id="",
            if_root=True,
            external_tool={
                "externalID": project,
                "name": jira_info["name"],
                "type": "Jira",
                "url": jira_info["url"],
                "urlSubpath": "browse/" + project
            })
    else:
        ids = {
            "baseline_original": externalTool[0]['project']['baselines'][0]['id'],
            "project": externalTool[0]['project']['id'],
            "project_baseline": externalTool[0]['project']['projectBaselines'][0]['id'],
            # "project_baseline_original": None
        }
        request_project_baseline_original = """
query v ($project_id: string, $baseline_id: string) {
  project_baseline_original (func: uid($baseline_id)) @normalize {
    Baseline.projects @filter(uid_in(ProjectBaseline.project, $project_id)) {
      id: uid
    }
  }
}
        """
        ids['project_baseline_original'] = request_dql_query(url, request_project_baseline_original, {"$project_id": ids['project'], "$baseline_id": ids['baseline_original']})['data']['project_baseline_original']
        if len(ids['project_baseline_original']) > 1:
            # print("ERROR: duplicated ID in the system: ", externalTool)
            raise Exception("ERROR: duplicated ID in the system: ", externalTool)
        else:
            ids['project_baseline_original'] = ids['project_baseline_original'][0]['id']


    # # issues = sync_issues_and_projects_by_jql(url, jira_info, "project=" + "pp and labels=p2_v3", ids['baseline_original']) # TODO: REMOVE
    # issues = sync_issues_and_projects_by_jql(url, jira_info, "project=" + "mc and type=task and component=be and fixVersion=1", ids['baseline_original']) # TODO: REMOVE
    # # issues = sync_issues_and_projects_by_jql(url, jira_info, "project=" + project, ids['baseline_original'])

    # # Sync base
    # sync_default_and_original_baseline(url, jira_info, issues, ids['project_baseline'], ids['baseline_original'], ids['project_baseline_original'])


    # TODO: fix parent start and finish dates
    query = """
query v ($root_id: string) {
  var (func: uid($root_id)) @recurse(loop: false) {
    ID as uid
    ProjectBaseline.children
  }
  
  projects (func: uid(ID)) @normalize {
    project_id: uid
    ProjectBaseline.parent { parent_id: uid }
    worktime: ProjectBaseline.worktime
    start: ProjectBaseline.start
    finish: ProjectBaseline.finish
  }
}
    """
    pbs = request_dql_query(url, query, {"$root_id": "[{0},{1}]".format(ids['project_baseline'], ids['project_baseline_original'])})

    solver = SolverBase(pd.DataFrame(pbs['data']['projects']))
    print(solver.projects[solver.projects.finish.notnull()])
    solver.update_projects(from_lp=False)
    print(solver.projects[solver.projects.finish.notnull()])
    
    

    return ids['project']






if __name__ == "__main__":

    url = "http://192.168.5.20:8080/"


    jira_info = {
        "name": "O2 jira",
        "url": "https://tangramcare.atlassian.net/",
        "username": "awaz@ownedoutcomes.com",
        "api_token": "6Pu9J7zSN4wBqwqgSREsAE08",
    }
 

    # root_id = import_project_from_jira(url, jira_info, "mc and component=FE and fixVersion=MVP")
    root_id = import_project_from_jira(url, jira_info, "PP")
    print("Root project id:", root_id)



    # project='tt'
    # print(create_project_pb_externaltool(
    #         url=url, 
    #         name=project, 
    #         original_baseline_id="",
    #         if_root=True,
    #         external_tool={
    #             "externalID": project,
    #             "name": jira_info["name"],
    #             "type": "Jira",
    #             "url": jira_info["url"],
    #             "urlSubpath": "browse/" + project
    #         }))

    # some custom solution to get original estimates









# %%
