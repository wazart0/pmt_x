import requests
import json
import rfc3339

import lib.jira.jira as jira











def sync_default_baseline_from_jira(baseline_id: str, url: str, jira_info: dict) -> None:

    query = '''
        query ($baseline_id :ID!) {
            getBaseline(id: $baseline_id) {
                projects {
                    id
                    project {customFields}
                }
            }
        }
    '''

    query_variables = {"baseline_id": baseline_id}

    mutation = '''
        mutation ($project_baseline_id: ID!, $fields: ProjectBaselinePatch!) {
            updateProjectBaseline (input: {filter: {id: [$project_baseline_id]} set: $fields}) {
                numUids
            }
        }
    '''


    r = requests.post(url=url, json={"query": query, "variables": query_variables})

    if r.status_code != 200 or 'errors' in r.json():
        print('ERROR: record not ingested: ' + str(url) + '\n' + str(r.status_code) + '\n' + str(r.json()) + '\n' + str(query))
        raise Exception('problem with getting data')



    for project in r.json()['data']['getBaseline']['projects']:
        if project['project']['customFields']:
            custom_fields = json.loads(project['project']['customFields'])
            if 'jira_id' in custom_fields:
                issue_changelog = jira.get_issue_changelog(jira_info, custom_fields['jira_id'])
                start = jira.get_issue_first_transition_date(issue_changelog, 'In Development')
                start = rfc3339.rfc3339(start) if start else None
                finish = jira.get_issue_last_transition_date(issue_changelog, 'Code Complete')
                finish = rfc3339.rfc3339(finish) if finish else None
                print(project['id'], custom_fields['jira_id'], start, finish)

                if start or finish:
                    variables = {
                        "project_baseline_id": project['id'],
                        "fields": {
                            "start": start,
                            "finish": finish
                        }
                    }
                    r = requests.post(url=url, json={"query": mutation, "variables": variables})
                    if r.status_code != 200 or 'errors' in r.json():
                        print('ERROR: record not ingested: ' + str(url) + '\n' + str(r.status_code) + '\n' + str(r.json()) + '\n' + str(mutation))
                        raise Exception('problem with getting data')

    print("Finished.")



if __name__ == "__main__":

    url = 'http://localhost:8080/graphql'


    jira_info = {
        'url': 'https://tangramcare.atlassian.net/',
        'username': 'awaz@ownedoutcomes.com',
        'api_token': '6Pu9J7zSN4wBqwqgSREsAE08',
    }

    baseline_id = "0x2df2"

    sync_default_baseline_from_jira(baseline_id, url, jira_info)
