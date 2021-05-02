#%%


import lib.pmtx_client.query_baselines as rb
# import lib.task_assignee_estimators.cpm_solver as base
import lib.task_assignee_estimators.last_finish_solver as base

import requests
import json
import pandas as pd
from time import time


url = 'http://localhost:8080/graphql'


query_project_filter = {
    "or": [
        {"name": {"allofterms": "P2 v3 Replatforming Tasks List.xlsx"}},
        {"name": {"allofterms": "O2 Grouper Pipeline - Task List.xlsx"}},
        {"name": {"allofterms": "P2 v3 Authorization_DS manager - list of tasks.xlsx"}}
    ]
}


normalized_baseline = rb.request_and_normalize_baselines_from_pmtx(url, query_project_filter)
dfp, dfd = rb.baseline_to_pandas_df(normalized_baseline)



query = '''
    query ($projects_ids:[ID!]) {
        queryProject (filter: {and: [{id: $projects_ids} ]}) {
            id
            customFields
        }
    }
'''

r = requests.post(url=url, json={"query": query, "variables": {"projects_ids": dfp.project_id.to_list()}})

project_details = r.json()['data']['queryProject']

for project in project_details:
    if project['customFields'] is not None:
        details = json.loads(project['customFields'])
        project['sprint'] = (int(details['sprint'].split(' ')[1]) if details['sprint'].split(' ')[1].isdigit() else None) if 'sprint' in details else None
    else: 
        project['sprint'] = None
    del project['customFields']

project_details = pd.DataFrame(project_details)
dfp = dfp.merge(project_details, how='left', left_on='project_id', right_on='id')
dfp.drop(columns=['id'], inplace=True)




est = base.LastFinishSolver(dfp,dfd)

est.config()

est.av = base.LastFinishSolver.create_availability_calendar(number_of_users=9)
est.av['project_id'] = None

algo_time_start = time()

est.initialize()
 

# print(est.allocate_projects_infinite_resources())
# print(est.create_wbs())
# dep = est.find_circular_dependencies()
# dep = est.assign()

# est.allocate_projects_infinite_resources()
dep = est.allocate_projects()




algo_time_finish = time()
print('Calculation time [s]: ' + str(algo_time_finish - algo_time_start))

print('\nCPMs:')
print(dep)

# %%
