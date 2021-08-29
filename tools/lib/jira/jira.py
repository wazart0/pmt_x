import requests
import dateutil.parser
import pytz
from datetime import datetime


# EXAMPLE jira_info: 
# jira_info = {
#     'url': 'https://xxx.atlassian.net/',
#     'username': 'user1',
#     'api_token': '6Pu9J7zSN4sgsdfREsAE08',
# }


def get_issues(jira_info: dict, jql: str) -> dict:

    max_results = 100
    start_at = 0
    response = requests.get('''https://tangramcare.atlassian.net/rest/api/2/search?jql={0}&maxResults={1}&startAt={2}'''.format(jql, max_results, start_at), auth=(jira_info['username'], jira_info['api_token'])).json()
    issues = response['issues']
    total = response['total']
    max_results = response['maxResults']

    while start_at < total:
        # return issues
        start_at = start_at + max_results
        response = requests.get('''https://tangramcare.atlassian.net/rest/api/2/search?jql={0}&maxResults={1}&startAt={2}'''.format(jql, max_results, start_at), auth=(jira_info['username'], jira_info['api_token'])).json()
        max_results = response['maxResults']
        issues = issues + response['issues']

    return issues


def get_issue_changelog(jira_info: dict, issue_key: str) -> dict:
    response = requests.get(jira_info['url'] + 'rest/api/2/issue/{0}/changelog'.format(issue_key), auth=(jira_info['username'], jira_info['api_token'])).json()
    changelog = response['values']
    while 'nextPage' in response:
        response = requests.get(response['nextPage'], auth=(jira_info['username'], jira_info['api_token'])).json()
        changelog = changelog + response['values']
    return changelog


def parse_date(date: str) -> datetime:
    return dateutil.parser.parse(date).astimezone(pytz.UTC)
    

def get_change_transition_date(change: dict, toStatus = None): # if toStatus is None return any status transition date
    if isinstance(toStatus, str):
        toStatus = [toStatus]
    for i in change['items']:
        if i['field'] == 'status': 
            if toStatus is None:            return parse_date(change['created']) 
            if i['toString'] in toStatus:   return parse_date(change['created']) 
    return None


def get_issue_first_transition_date(issueCL: dict, toStatus: str):
    for change in reversed(issueCL):
        date = get_change_transition_date(change, toStatus)
        if date is not None:    return date
    return None


def get_issue_last_transition_date(issueCL: dict, toStatus: str):
    for change in issueCL:
        date = get_change_transition_date(change, toStatus)
        if date is not None:    return date
    return None

    