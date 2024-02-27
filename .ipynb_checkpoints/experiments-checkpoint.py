#%%

import requests
import json
import pandas as pd
from time import time
import rfc3339
from atlassian import Jira

import tools.lib.jira.jira as jira



def sync_baseline_to_jira(baseline_id: str, url: str, jira_info: dict) -> None:
    jira = Jira(
        url=jira_info['url'],
        username=jira_info['username'],
        password=jira_info['api_token'],
        cloud=True)

    query = '''
        query ($baseline_id :ID!) {
            getBaseline(id: $baseline_id) {
                projects {
                    id
                    start
                    finish
                }
                
            }
        }
    '''

    query_variables = {"baseline_id": baseline_id}


    r = requests.post(url=url, json={"query": query, "variables": query_variables})

    if r.status_code != 200 or 'errors' in r.json():
        print('ERROR: record not ingested: ' + str(url) + '\n' + str(r.status_code) + '\n' + str(r.json()) + '\n' + str(query))
        raise Exception('problem with getting data')


    for project in r.json()['data']['getBaseline']['projects']:
        pass




if __name__ == "__main__":

    url = 'http://localhost:8080/graphql'


    jira_info = {
        'url': 'https://tangramcare.atlassian.net/',
        'username': 'awaz@ownedoutcomes.com',
        'api_token': '6Pu9J7zSN4wBqwqgSREsAE08',
    }

    baseline_id = "0x2df2"

    sync_baseline_to_jira(baseline_id, url, jira_info)






# %%
