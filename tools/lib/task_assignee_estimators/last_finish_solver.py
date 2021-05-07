import pandas as pd
from tools.lib.task_assignee_estimators.solver_base import SolverBase, SolverBaseResources

from time import time



class LastFinishSolver(SolverBaseResources): ## ideological reasons caused stop working on this. The idea to be reviewed later.

    def __init__(self, projects = None, dependencies = None, availability = None):
        super().__init__(projects, dependencies, availability)


    def allocate_projects(self, create_plan_from_scratch = True, exclude_projects = []): # TODO: add exclude/include projects
        self.infinite_plan = SolverBase()
        self.infinite_plan.lp = self.lp.copy(deep=True)
        self.infinite_plan.ld = self.ld.copy(deep=True)

        self.infinite_plan.allocate_projects_infinite_resources()

        if create_plan_from_scratch:
            self.lp.start = None
            self.lp.finish = None

        while True:

            window = self.infinite_plan.lp[self.infinite_plan.lp.project_id.isin(self.lp[self.lp.finish.isnull()].project_id)]
            last_finish_unallocated = window[window.finish == window.finish.max()].project_id

            if len(last_finish_unallocated) == 0: 
                break

            # if 
            self.allocate_project_and_its_predecesors(last_finish_unallocated.iat[0], exclude_projects)




    def get_dependency_ancestors(self, project_id):
        predecessors = self.ld[self.ld.project_id == project_id].predecessor_id.to_list()
        dependency_ancestors = set(predecessors)
        
        while predecessors: # traverse through predecessors
            predecessors = self.ld[self.ld.project_id.isin(predecessors)].predecessor_id.to_list()
            dependency_ancestors.update(predecessors)

        return dependency_ancestors


    def get_first_free_resource_id(self, from_date: pd.Timestamp):
        # return self.av[self.av.project_id.isnull() & (self.av.start == self.av[self.av.project_id.isnull()].start.min())].resource_id.iat[0]
        return self.av[self.av.project_id.isnull() & (from_date <= self.av.start)].sort_values(['start']).resource_id.iat[0]


    def allocate_project_and_its_predecesors(self, project_id, exclude_projects = []): # allocate predecessors in some way
        projects_in_branch = self.get_dependency_ancestors(project_id)
        projects_in_branch.add(project_id)
        print('Projects in tree:', projects_in_branch)
        print('Number of projects in tree:', len(projects_in_branch))

        if len(projects_in_branch) == 1: # if no predecessors then assign
            if self.lp[(self.lp.project_id == project_id) & self.lp.finish.notnull()].shape[0] == 0 and project_id not in exclude_projects: ## allocate if not allocated yet
                resource_id = [self.get_first_free_resource_id(self.project_start)]
                self.assign_time_first_free(project_id, resource_id, self.project_start)
            return


        ## projects without any dependencies for initial round
        projects_to_allocate = self.ld[(~self.ld.predecessor_id.isin(self.ld.project_id)) & self.ld.project_id.isin(projects_in_branch)].predecessor_id.unique()

        for p_id in projects_to_allocate:
            if self.lp[(self.lp.project_id == p_id) & self.lp.finish.notnull()].shape[0] == 0 and project_id not in exclude_projects: ## allocate if not allocated yet
                resource_id = [self.get_first_free_resource_id(self.project_start)]
                self.assign_time_first_free(p_id, resource_id, self.project_start)

        iter = 0

        projects_to_allocate_next_iter = []

        while iter < 2:
            projects_to_allocate = list(self.ld[self.ld.predecessor_id.isin(projects_to_allocate) & self.ld.project_id.isin(projects_in_branch)].project_id.unique()) # get successors
            projects_to_allocate = projects_to_allocate_next_iter + projects_to_allocate

            if len(projects_to_allocate) == 0:
                break

            projects_to_allocate_next_iter = []
            for p_id in projects_to_allocate:
                if self.lp[(self.lp.project_id == p_id) & self.lp.finish.notnull()].shape[0] == 0 and project_id not in exclude_projects: ## allocate if not allocated yet
                    if self.lp[self.lp.project_id.isin(self.ld[self.ld.project_id == p_id].predecessor_id) & self.lp.finish.isnull()].shape[0] > 0:
                        projects_to_allocate_next_iter.append(p_id)
                        continue
                    predecessor_finish = self.lp[self.lp.project_id.isin(self.ld[self.ld.project_id == p_id].predecessor_id)].finish.max()
                    resource_id = [self.get_first_free_resource_id(predecessor_finish)]
                    self.assign_time_first_free(p_id, resource_id, predecessor_finish)

            # projects_to_allocate = self.ld[self.ld.predecessor_id.isin(projects_to_allocate)].project_id.unique()                
            
            # iter = iter + 1

        print('Final number of allocated projects:', self.lp[self.lp.finish.notnull()].shape[0])
        print()
        # return projects_to_allocate, projects_to_allocate_next_iter

