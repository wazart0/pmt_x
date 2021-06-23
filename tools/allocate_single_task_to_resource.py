import lib.pmtx_client.query_baseline as rb
import requests
import json
import pandas as pd
from time import time



def get_dfp_dfd(url, baseline_id):

    normalized_baseline = rb.request_and_normalize_baseline_from_pmtx(url, baseline_id)
    dfp, dfd, dfr = rb.baseline_to_pandas_df(normalized_baseline)

    print("acquiring completed.")

    return dfp, dfd, dfr



def assign_project(dfp, dfd, dfr, project_id):
    import lib.task_assignee_estimators.solver_base as estimator

    solver = estimator.SolverBaseResources(dfp.copy(deep=True), dfd.copy(deep=True), dfr.copy(deep=True))

    solver.config()
    solver.initialize()

    if solver.lp[solver.lp.project_id == project_id].shape[0] == 0:
        err_msg = "it is not lowest level project"
        print(err_msg, project_id)
        return solver, err_msg

    if solver.lp[(solver.lp.project_id == project_id) & solver.lp.worktime.isnull()].shape[0]:
        err_msg = "project doesn't have worktime planned"
        print(err_msg, project_id)
        return solver, err_msg

    if solver.lp[(solver.lp.project_id == project_id) & (solver.lp.start.isnull() | solver.lp.finish.isnull())].shape[0] == 0:
        err_msg = "project start or finish is already assigned"
        print(err_msg, project_id)
        return solver, err_msg

    if solver.av[solver.av.project_id == project_id].shape[0] != 0:
        err_msg = "project already assigned in calendar"
        print(err_msg, project_id)
        return solver, err_msg

    if solver.lp[solver.lp.project_id.isin(solver.ld[solver.ld.project_id == project_id].predecessor_id) & solver.lp.finish.isnull()].shape[0]:
        err_msg = "predecessor is not assigned for project"
        print(err_msg, project_id, "(list:", solver.lp[solver.lp.project_id.isin(solver.ld[solver.ld.project_id == project_id].predecessor_id) & solver.lp.finish.isnull()].project_id.to_list(), ")")
        return solver, (err_msg + " (predecessors:" + str(solver.lp[solver.lp.project_id.isin(solver.ld[solver.ld.project_id == project_id].predecessor_id) & solver.lp.finish.isnull()].project_id.to_list()) + ")")

    if solver.ld[solver.ld.type != 'FS'].shape[0] != 0:
        err_msg = "Project doesn't serve other than FS dependencies"
        print(err_msg, project_id)
        return solver, err_msg

    # print(solver.av)

    av_cal = estimator.SolverBaseResources.create_availability_calendar(start_time=pd.Timestamp.now(tz='UTC'), number_of_users=5)
    av_cal['project_id'] = None
    solver.av = solver.merge_calendars(solver.av, av_cal)


    if solver.ld[solver.ld.project_id == project_id].shape[0]:
        minimal_project_start = solver.lp[solver.lp.project_id.isin(solver.ld[solver.ld.project_id == project_id].predecessor_id)].finish.max()
    else:
        minimal_project_start = solver.lp.start.min()
    
    resource_id = [solver.get_first_free_resource_id(minimal_project_start)]

    # print(solver.lp)
    # print(minimal_project_start, resource_id)

    solver.allocate_time_continuous_per_project(project_id, resource_id, minimal_project_start)

    solver.update_projects()

    # print(solver.lp[solver.lp.project_id == project_id])
    # print(solver.av[solver.av.project_id.notnull()])

    return solver, None




def send_to_pmtx(url, solver, baseline_id):
    import lib.pmtx_client.mutate_baselines as mb
    import datetime

    root_id = mb.cleanup_baseline(url, baseline_id)

    mb.add_project_baseline(url, solver.projects, baseline_id, root_id)
    mb.modify_project_baseline_predecessors(url, solver.dependencies, baseline_id)
    mb.add_resource_baseline(url, solver.av, baseline_id)

    print("Finished.")



if __name__ == "__main__":

    url = 'http://localhost:8080/graphql'

    baseline_id = "0xccc"

    project_id = "0xa1"



    dfp, dfd, dfr = get_dfp_dfd(url, baseline_id)

    solver = assign_project(dfp, dfd, dfr, project_id)

    print(solver.av[solver.av.project_id.notnull()])

    # send_to_pmtx(url, solver, baseline_id)



    