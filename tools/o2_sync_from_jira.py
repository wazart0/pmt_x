# %%
import requests
import pickle
import json
import rfc3339

import lib.jira.jira as jira
from lib.pmtx_client.pmtx_base import request_dql_mutate, request_gql






def create_project_pb_externaltool(url: str, name: str, description = None, external_tool = {}) -> dict:

    # project_description = "" # TODO: resolve issue with serialization
    project_description = '_:project <Project.description> {0} .'.format(json.dumps(description)) if description else ""

    create_project = '''
{
  set {
    _:project <dgraph.type> "Project" .
    _:project <Project.name> {name} .
    {project_description}
    _:project <Project.baseline> _:project_baseline .
    _:project <Project.externalTool> _:exttool .
    
    _:project_baseline <dgraph.type> "ProjectBaseline" .
    _:project_baseline <ProjectBaseline.project> _:project .

    {ExternalTool}
  }
}
    '''. \
        replace("{name}", json.dumps(name)). \
        replace("{project_description}", project_description)


    exttool = ""
    if external_tool:
        exttool = """
    _:exttool <dgraph.type> "ExternalTool" .
    _:exttool <ExternalTool.project> _:project .
    _:exttool <ExternalTool.externalID> "{externalID}" .
    _:exttool <ExternalTool.name> "{name}" .
    _:exttool <ExternalTool.type> "{type}" .
    _:exttool <ExternalTool.url> "{url}" .
    _:exttool <ExternalTool.urlSubpath> "{urlSubpath}" .
        """. \
            replace("{externalID}", external_tool['externalID']). \
            replace("{name}", external_tool['name']). \
            replace("{type}", external_tool['type']). \
            replace("{url}", external_tool['url']). \
            replace("{urlSubpath}", external_tool['urlSubpath'])
    
    if 'customFields' in external_tool:
        exttool = exttool + """_:exttool <ExternalTool.customFields> {0} .""".format(json.dumps(external_tool['customFields']))
        
    create_project = create_project.replace("{ExternalTool}", exttool)
    
    response = request_dql_mutate(url, create_project)

    return {
        "project_id": response['data']['uids']['project'], 
        "project_baseline_id": response['data']['uids']['project_baseline']
    }





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






def sync_issues_and_projects_by_jql(url: str, jira_info: dict, jql: str):

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
                "urlSubpath": "rest/api/2/issue/" + issue["key"],
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
      filter: {id: [$id]}
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
            # issue['baseline'] = {}
            projects_to_create.append(issue)


    for issue in projects_to_create:
        # response = request_gql(url, create_projects, {"projects": projects_to_create})
        create_project_pb_externaltool(url, issue['name'], issue['description'], issue['externalTool'][0])

    return issues





## TODO: add parent when epic, task, sub-task (as higher priority compared to links)
def sync_default_baseline(url: str, jira_info: dict, issues: dict, baseline_root_id = None): 

    query = """
query ($jira_ids: [String!]!) {
  queryExternalTool (filter: {externalID: {in: $jira_ids}}) {
    externalID
    project {baseline {id}}
  }
}
    """
    response = request_gql(url, query, {"jira_ids": [issue['key'] for issue in issues]})
    map_jira_pmt = {}
    for i in response['data']['queryExternalTool']:
        map_jira_pmt[i['externalID']] = i['project']['baseline']['id']

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

            if issue['fields']['issuetype']['name'] == "Sub-task":
                if issue['fields']['parent']['key'] in map_jira_pmt:
                    pb['parent'] = {'id': map_jira_pmt[issue['fields']['parent']['key']]}
                else:
                    print("WARNING: parent not in map [current, parent]:", issue['key'], '->', issue['fields']['parent']['key'])


            for link in issue['fields']['issuelinks']:
                if link['type']['inward'] == 'split from' and 'inwardIssue' in link:
                    if link['inwardIssue']['key'] in map_jira_pmt:
                        pb['parent'] = {"id": map_jira_pmt[link['inwardIssue']['key']]}
                    else:
                        print("WARNING: parent not in map [current, parent]:", issue['key'], '->', link['inwardIssue']['key'])
                if link['type']['inward'] == 'has to be done after' and 'inwardIssue' in link:
                    if link['inwardIssue']['key'] in map_jira_pmt:
                        if 'predecessors' not in pb: pb['predecessors'] = []
                        pb['predecessors'].append({
                            "type": "FS",
                            "project": {"id": map_jira_pmt[link['inwardIssue']['key']]}
                            })
                    else:
                        print("WARNING: predecessor not in map [current, predecessor]:", issue['key'], '->', link['inwardIssue']['key'])


            # if issue['fields']['timeoriginalestimate']:
            #     pb['worktime'] = str(issue['fields']['timeoriginalestimate']/3600.) + 'h'
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

            if baseline_root_id is not None and 'parent' not in pb:
                pb['parent'] = {"id": baseline_root_id}

            if pb: 
                request_gql(url, mutation, {
                    "project_baseline_id": map_jira_pmt[issue['key']],
                    "fields": pb
                })

    return




# WARNING: needs refinement before start using, probably doesn't make any sense
# def sync_baseline(url: str, jira_info: dict, issues: dict, baseline_id: str, fields_map: dict):

#     query = """
# query ($jira_ids: [String!]! $baseline_id: ID!) {
#   queryExternalTool (filter: {externalID: {in: $jira_ids}}) {
#     externalID
#     project {baselines (filter: {id: [$baseline_id]}) {projects {id}}}
#   }
# }
#     """
#     response = request_gql(url, query, {"jira_ids": [issue['key'] for issue in issues]})
#     map_jira_pmt = {}
#     for i in response['data']['queryExternalTool']:
#         map_jira_pmt[i['externalID']] = i['project']['baseline']['id']

#     mutation = """
# mutation ($project_baseline_id: ID!, $fields: ProjectBaselinePatch!) {
#   updateProjectBaseline (input: {filter: {id: [$project_baseline_id]} set: $fields}) {
#     numUids
#   }
# }
#     """

#     for issue in issues:
#         if issue['key'] in map_jira_pmt:
#             pb = {}

#             if 'parent' in fields_map:
#                 for link in issue['fields']['issuelinks']:
#                     if link['type']['inward'] == fields_map['parent'] and 'inwardIssue' in link:
#                         pb['parent'] = {"id": map_jira_pmt[link['inwardIssue']['key']]}

#             if 'worktime' in fields_map and issue['fields'][fields_map['worktime']]:
#                 pb['worktime'] = str(issue['fields']['timespent']/3600) + 'h'

#             # if issue['fields']['customfield_11737']: 
#             #   pb['start'] = rfc3339.rfc3339(issue['fields']['customfield_11737'])
#             # if issue['fields']['customfield_11737']: 
#             #   pb['finish'] = rfc3339.rfc3339(issue['fields']['customfield_11737'])

#             if pb: 
#                 request_gql(url, mutation, {
#                     "project_baseline_id": map_jira_pmt[issue['key']],
#                     "fields": pb
#                 })

#     return



    



def import_project_from_jira(url: str, jira_info: dict, project: str) -> str:
    issues = sync_issues_and_projects_by_jql(url, jira_info, "project=" + project)

    get_already_existing_issues = '''
query ($jiraIDs: [String!]! $url: String!) {
  queryExternalTool (filter: {and: [{externalID: {in: $jiraIDs}} {url: {eq: $url}}]}) {
    externalID
    project { 
      id
      baseline { id }
    }
  }
}
    '''
    response = request_gql(url, get_already_existing_issues, {"jiraIDs": [issues[0]['fields']['project']['key']], "url": jira_info['url']})

    if response['data']['queryExternalTool']:
        ids = {
            'project_id': response['data']['queryExternalTool'][0]['project']['id'],
            'project_baseline_id': response['data']['queryExternalTool'][0]['project']['baseline']['id'],
        }
    else:
        ids = create_project_pb_externaltool(
            url=url, 
            name=issues[0]['fields']['project']['name'], 
            external_tool = {
                "externalID": issues[0]['fields']['project']['key'],
                "name": jira_info["name"],
                "type": "Jira",
                "url": jira_info["url"],
                "urlSubpath": issues[0]['fields']['project']['self']
            })

    sync_default_baseline(url, jira_info, issues, ids['project_baseline_id'])

    return ids['project_id']






if __name__ == "__main__":

    url = "http://192.168.5.20:8080/"


    jira_info = {
        "name": "O2 jira",
        "url": "https://tangramcare.atlassian.net/",
        "username": "awaz@ownedoutcomes.com",
        "api_token": "6Pu9J7zSN4wBqwqgSREsAE08",
    }


    # root_id = import_project_from_jira(url, jira_info, "mc and component=FE and fixVersion=MVP")
    root_id = import_project_from_jira(url, jira_info, "pp and labels=p2_v3")

    print("Root project id:", root_id)


    # some custom solution to get original estimates









# %%
