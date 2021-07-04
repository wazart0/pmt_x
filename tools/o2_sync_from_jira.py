# %%
import requests
import json
import rfc3339

import lib.jira.jira as jira



def request_gql(url: str, query: str, variables: dict) -> dict:
    r = requests.post(url=url + 'graphql', json={"query": query, "variables": variables})
    if r.status_code != 200 or "errors" in r.json():
        # print("ERROR: record not ingested: " + str(url) + "\n" + str(r.status_code) + "\n" + str(r.json()) + "\n" + str(query))
        print("ERROR:")
        print("Problem occured while sinding to PMT X:")
        print("URL:", url)
        print("QUERY:", query)
        print("VARIABLES:")
        print(json.dumps(variables, indent=4))
        print("RESPONSE:")
        print(json.dumps(r.json(), indent=4))
        raise Exception("Problem occured while sinding to PMT X")
    return r.json()






def sync_baseline_from_jira(baseline_id: str, url: str, jira_info: dict) -> None:

    query = """
        query ($baseline_id :ID!) {
            getBaseline(id: $baseline_id) {
                projects {
                    id
                    project {customFields}
                }
            }
        }
    """

    query_variables = {"baseline_id": baseline_id}


    r = requests.post(url=url, json={"query": query, "variables": query_variables})
    if r.status_code != 200 or "errors" in r.json():
        print("ERROR: record not ingested: " + str(url) + "\n" + str(r.status_code) + "\n" + str(r.json()) + "\n" + str(query))
        raise Exception("problem with getting data")





    mutation = """
        mutation ($project_baseline_id: ID!, $fields: ProjectBaselinePatch!) {
            updateProjectBaseline (input: {filter: {id: [$project_baseline_id]} set: $fields}) {
                numUids
            }
        }
    """

    for project in r.json()["data"]["getBaseline"]["projects"]:
        if project["project"]["customFields"]:
            custom_fields = json.loads(project["project"]["customFields"])
            if "jira_id" in custom_fields:
                issue_changelog = jira.get_issue_and_changelog(jira_info, custom_fields["jira_id"])
                start = jira.get_issue_first_transition_date(issue_changelog, "In Development")
                start = rfc3339.rfc3339(start) if start else None
                finish = jira.get_issue_last_transition_date(issue_changelog, "Code Complete")
                finish = rfc3339.rfc3339(finish) if finish else None
                print(project["id"], custom_fields["jira_id"], start, finish)

                if start or finish:
                    variables = {
                        "project_baseline_id": project["id"],
                        "fields": {
                            "start": start,
                            "finish": finish
                        }
                    }
                    r = requests.post(url=url, json={"query": mutation, "variables": variables})
                    if r.status_code != 200 or "errors" in r.json():
                        print("ERROR: record not ingested: " + str(url) + "\n" + str(r.status_code) + "\n" + str(r.json()) + "\n" + str(mutation))
                        raise Exception("problem with getting data")

    print("Finished.")




def sync_issues_and_projects(url: str, jira_info: dict, jql: str):

    issues = jira.get_issues(jira_info, jql)
    parsed_issues = []
    for issue in issues:
        parsed = {
            "name": issue["fields"]["summary"],
            "description": issue["fields"]["description"],
            "externalTool": [{
                "externalID": issue["key"],
                "name": "o2 jira",
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
            issue['baseline'] = {}
            projects_to_create.append(issue)

    create_projects = '''
mutation ($projects: [AddProjectInput!]!) {
  addProject (input: $projects) {
    numUids
  }
}
    '''

    if projects_to_create:
        response = request_gql(url, create_projects, {"projects": projects_to_create})

    return [issue['key'] for issue in issues]



def sync_default_baseline(url: str, jira_info: dict, issues_keys: list):

    for key in issues_keys:
        issueCL = jira.get_issue_changelog(jira_info, key)
        baseline = {
            "start": jira.get_issue_first_transition_date(issueCL, ["In progress"]),
            "finish": jira.get_issue_last_transition_date(issueCL, ["Closed"]),
            # "worktime": 
        }


    return




if __name__ == "__main__":

    url = "http://localhost:8080/"


    jira_info = {
        "url": "https://tangramcare.atlassian.net/",
        "username": "awaz@ownedoutcomes.com",
        "api_token": "6Pu9J7zSN4wBqwqgSREsAE08",
    }

    # baseline_id = "0x2df2"

    # sync_baseline_from_jira(baseline_id, url, jira_info)

    p = sync_issues_and_projects(url, jira_info, "project=pp and labels=p2_v3")





# %%
