

def get_dfp_dfd():
    import lib.pmtx_client.query_baselines as rb
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

    print("acquiring completed.")

    return dfp, dfd



def generate_estimation(dfp, dfd):

    from time import time
    import pandas as pd

    import lib.task_assignee_estimators.last_finish_solver as estimator


    dfp, dfd = get_dfp_dfd()

    solver = estimator.LastFinishSolver(dfp.copy(deep=True),dfd.copy(deep=True))

    solver.config()


    solver.av = estimator.LastFinishSolver.create_availability_calendar(start_time=pd.Timestamp('2021-05-02 21:04:56.092887+0000'), number_of_users=5)

    solver.av['project_id'] = None
    print(solver.av.shape[0])

    # Calculation part

    solver.initialize()


    algo_time_start = time()


    finish_date = solver.allocate_projects(create_plan_from_scratch=False)
    # finish_date = solver.allocate_projects(create_plan_from_scratch=False, exclude_projects=solver.lp[solver.lp.sprint != 6].project_id.to_list())
    # finish_date = solver.assign_projects_to_resources_first_free(one_worker_per_project=True)
    # finish_date = solver.assign_projects_by_start_based_on_infinite_resources(one_worker_per_project=True)
    # finish_date = solver.assign_projects_by_start_based_on_infinite_resources(partial_update=True, partial_update_from=pd.Timestamp('2021-01-01', tz='UTC'), one_worker_per_project=True)

    print(solver.av.shape[0])
    solver.update_projects()

    algo_time_finish = time()

    print('Project finish timestamp: ' + str(finish_date))
    print('Calculation time [s]: ' + str(algo_time_finish - algo_time_start))
    # print('Unassigned workers time during project: ' + str((solver.av[solver.av.project_id.isnull() & (solver.av.start <= finish_date)].finish - solver.av[solver.av.project_id.isnull() & (solver.av.start <= finish_date)].start).sum()))

    print("Finished.")

    return solver





def send_to_pmtx(solver):
    import lib.pmtx_client.mutate_baselines as mb
    import datetime

    url = 'http://localhost:8080/graphql'

    solver.projects.drop(columns=['sprint'], inplace=True)

    root_id = "0x2e8a"
    baseline_name = "X last finish solver - not finished " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    baseline_id = mb.add_baseline_and_return_id(url, baseline_name, root_id)
    mb.add_project_baseline(url, solver.projects, baseline_id, root_id)
    mb.modify_project_baseline_predecessors(url, solver.dependencies, baseline_id)
    mb.add_resource_baseline(url, solver.av, baseline_id)

    print("Finished.")



if __name__ == "__main__":

    dfp, dfd = get_dfp_dfd()

    send_to_pmtx(generate_estimation(dfp, dfd))



    