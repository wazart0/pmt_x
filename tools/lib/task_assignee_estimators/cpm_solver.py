import pandas as pd
from lib.task_assignee_estimators.solver_base import SolverBase, SolverBaseResources

from time import time



class CPMsolver(SolverBaseResources): ## ideological reasons caused stop working on this. The idea to be reviewed later.

    def __init__(self, projects = None, dependencies = None, availability = None):
        super().__init__(projects, dependencies, availability)


    def allocate_projects(self):
        self.infinite_plan = SolverBase()
        self.infinite_plan.lp = self.lp.copy(deep=True)
        self.infinite_plan.ld = self.ld.copy(deep=True)

        self.infinite_plan.allocate_projects_infinite_resources()

        self.lp.start = None
        self.lp.finish = None

        exclude_projects = []

        t = time()
        time_start = t
        total_amount_of_fixes = 0

        i = 0
        while True:
            cpms = self.infinite_plan.get_cpm(exclude_projects)
            # print(cpms)

            if not cpms:
                break

            # for cpm in cpms:
            #     if cpm[0] not in exclude_projects:
            #         exclude_projects.append(cpm[0])

            #     resource_id = [self.get_first_free_resource_id()]

                # for project_id in cpm[::-1]:
                #     if self.av[self.av.project_id == project_id].shape[0] == 0:
                        # self.assign_time_first_free(project_id, resource_id, self.av.start.min())
                
            # total_amount_of_fixes = total_amount_of_fixes + self.fix_dependence_issues()


            p = self.allocate_project_and_its_predecesors(cpms[0][0])


            if i % 1 == 0:
                print('Iter:', i, '(number of excluded projects: ', len(exclude_projects), ')')
                print('Time spent in current iter:', time() - t, '(total time:', time() - time_start, ')')
                print('Incorrectly allocated depends:', self.find_incorrectly_allocated_projects_FS().shape[0])
                print('Total amount of dependence fixes:', total_amount_of_fixes)
                print('')
                t = time()

            i = i + 1

            return p


    def get_first_free_resource_id(self, from_date: pd.Timestamp):
        # return self.av[self.av.project_id.isnull() & (self.av.start == self.av[self.av.project_id.isnull()].start.min())].resource_id.iat[0]
        return self.av[self.av.project_id.isnull() & (from_date <= self.av.start)].sort_values(['start']).resource_id.iat[0]


    def allocate_project_and_its_predecesors(self, project_id):
        predecessors = self.ld[self.ld.project_id == project_id].predecessor_id.to_list()
        x = set(predecessors)

        # traverse through predecessors
        while predecessors:
            predecessors = self.ld[self.ld.project_id.isin(predecessors)].predecessor_id.to_list()
            x.update(predecessors)

        ## projects without any dependencies for initial round
        projects_to_allocate = self.ld[(~self.ld.predecessor_id.isin(self.ld.project_id)) & self.ld.project_id.isin(x)].predecessor_id.unique()

        for p_id in projects_to_allocate:
            if self.av[self.av.project_id == p_id].shape[0] == 0: ## allocate if not allocated yet
                resource_id = [self.get_first_free_resource_id(self.project_start)]
                self.assign_time_first_free(p_id, resource_id, self.project_start)

        p = [projects_to_allocate]

        while len(projects_to_allocate):
            projects_to_allocate = self.ld[self.ld.predecessor_id.isin(projects_to_allocate)].project_id.unique()
            p.append(projects_to_allocate)

            for p_id in projects_to_allocate:
                if self.av[self.av.project_id == p_id].shape[0] == 0: ## allocate if not allocated yet
                    predecessor_finish = self.lp[self.lp.project_id.isin(self.ld[self.ld.project_id == p_id].predecessor_id)].finish.max()
                    resource_id = [self.get_first_free_resource_id(predecessor_finish)]
                    self.assign_time_first_free(p_id, resource_id, predecessor_finish)


            
            return p

        # return x


    def reallocate_project(self, project_id): # works with FS dependencies
        self.unassign_project_from_resources(project_id)
        start_min = self.lp[self.lp.finish.notnull() & self.lp.project_id.isin(self.ld[self.ld.project_id == project_id].predecessor_id)].finish.max()
        window = self.av[(self.av.start >= start_min) & self.av.project_id.isnull()]
        resource_id = window[window.start == window.start.min()].resource_id.iat[0]

        self.assign_time_first_free(project_id, [resource_id], self.av.start.min())


    def fix_dependence_issues(self):
        number_of_fixes = 0
        while True: # fix dependency issue
            update = self.find_incorrectly_allocated_projects_FS()

            if update.shape[0] == 0:
                return number_of_fixes

            self.reallocate_project(update.project_id.iat[0])

            number_of_fixes += 1

