import pandas as pd
from lib.task_assignee_estimators.solver_base import SolverBase, SolverBaseResources

from time import time



class CPMsolver(SolverBaseResources):

    def __init__(self, projects = None, dependencies = None, availability = None):
        super().__init__(projects, dependencies, availability)


    def assign(self):
        infinite_plan = SolverBase()
        infinite_plan.lp = self.lp.copy(deep=True)
        infinite_plan.ld = self.ld.copy(deep=True)

        infinite_plan.allocate_projects_infinite_resources()

        self.lp.start = None
        self.lp.finish = None

        exclude_projects = []

        t = time()
        time_start = t

        i = 0
        while True:
            cpms = infinite_plan.get_cpm(exclude_projects)
            print(cpms)

            if not cpms:
                break

            for cpm in cpms:
                if cpm[0] not in exclude_projects:
                    exclude_projects.append(cpm[0])

                resource_id = [self.get_first_free_resource_id()]

                for project_id in cpm[::-1]:
                    if self.av[self.av.project_id == project_id].shape[0] == 0:
                        self.assign_time_first_free(project_id, resource_id)


            if i % 200 == 0:
                print('Iter:', i, '(number of excluded projects: ', len(exclude_projects), ')')
                print('Time spent in current iter:', time() - t, '(total time:', time() - time_start, ')')
                print('Incorrectly allocated depends:', self.find_incorrectly_allocated_projects_FS().shape[0])
                t = time()

            i = i + 1

        return 


    def get_first_free_resource_id(self):
        return self.av[self.av.project_id.isnull() & (self.av.start == self.av[self.av.project_id.isnull()].start.min())].resource_id.iat[0]


    def reallocate_project(self, project_id):
        self.unassign_project_from_resources(project_id)
        dependencies = self.ld[self.ld.project_id == project_id].copy(deep=True)
        start_min = dependencies.merge(self.lp[['project_id', 'finish']], how='left', left_on='predecessor_id', right_on='project_id').finish.max()
        # window = self.av[self.av.start >= start_min & self.av.project_id.isnull()]
        # resource_id = window[window.start == window.start.min()].resource_id.iat[0]

        # add partial update assign_time_first_free(self, project_id, from_date = None, assignee = None, one_worker_per_project = False)



