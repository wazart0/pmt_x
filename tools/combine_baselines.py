import lib.pmtx_client.query_baseline as rb
import requests
import json
import pandas as pd
from time import time



def get_dfp_dfd(url, baseline_id, merged_baseline_id):

    normalized_baseline = rb.request_and_normalize_baseline_from_pmtx(url, baseline_id)
    dfp, dfd, dfr = rb.baseline_to_pandas_df(normalized_baseline)

    normalized_baseline = rb.request_and_normalize_baseline_from_pmtx(url, merged_baseline_id)
    mdfp, mdfd, mdfr = rb.baseline_to_pandas_df(normalized_baseline)

    print("acquiring completed.")

    return dfp, dfd, dfr, mdfp, mdfd, mdfr



def combiner(dfp, dfd, dfr, mdfp, mdfd, mdfr):
    import lib.task_assignee_estimators.solver_base as estimator

    solver = estimator.SolverBaseResources(dfp.copy(deep=True), dfd.copy(deep=True), dfr.copy(deep=True))

    print(solver.projects[solver.projects.worktime.notnull()].shape[0])

    for index, row in solver.projects.iterrows():
        if row['worktime'] is pd.Timedelta(None):
            mdfp_index = mdfp[mdfp.project_id == row['project_id']].index[0]
            solver.projects.loc[index, 'worktime'] = mdfp.loc[mdfp_index, 'worktime']

    solver.update_projects(from_lp=False)
    
    print(solver.projects[solver.projects.worktime.notnull()].shape[0])

    print("Finished.")
    return solver





def send_to_pmtx(url, solver, baseline_id):
    import lib.pmtx_client.mutate_baselines as mb
    import datetime

    root_id = rb.get_root_id(url, baseline_id)
    baseline_name = "X test " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    baseline_id = mb.add_baseline_and_return_id(url, baseline_name, root_id)
    mb.add_project_baseline(url, solver.projects, baseline_id, root_id)
    mb.modify_project_baseline_predecessors(url, solver.dependencies, baseline_id)
    mb.add_resource_baseline(url, solver.av, baseline_id)

    print("Finished.")



if __name__ == "__main__":

    url = 'http://localhost:8080/graphql'

    baseline_id = "0x6b"

    merged_baseline_id = "0x403"




    dfp, dfd, dfr, mdfp, mdfd, mdfr = get_dfp_dfd(url, baseline_id, merged_baseline_id)

    solver = combiner(dfp, dfd, dfr, mdfp, mdfd, mdfr)

    send_to_pmtx(url, solver, baseline_id)

    