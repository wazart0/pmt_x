#%%

import requests
import json
import pandas as pd
from time import time
import rfc3339

import tools.lib.jira.jira as jira







if __name__ == "__main__":

    url = 'http://localhost:8080/graphql'


    jira_info = {
        'url': 'https://tangramcare.atlassian.net/',
        'username': 'awaz@ownedoutcomes.com',
        'api_token': '6Pu9J7zSN4wBqwqgSREsAE08',
    }

    baseline_id = "0x2df2"




# %%
