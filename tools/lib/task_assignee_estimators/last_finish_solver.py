import pandas as pd
from lib.task_assignee_estimators.solver_base import SolverBase, SolverBaseResources

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

            window = self.infinite_plan.lp[self.infinite_plan.lp.project_id.isin(self.lp[self.lp.finish.isnull()].project_id) & (~self.infinite_plan.lp.project_id.isin(exclude_projects))]
            print(window.project_id.to_list())
            last_finish_unallocated = window[window.finish == window.finish.max()].project_id

            if len(last_finish_unallocated) == 0: 
                break

            result = self.allocate_project_and_its_predecesors(last_finish_unallocated.iat[0], exclude_projects)
            if result == False and len(exclude_projects) != 0:
                exclude_projects = exclude_projects + [last_finish_unallocated.iat[0]]






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


    def allocate_project_first_fitting(self, project_id: str, minimal_project_start: pd.Timestamp, exclude_projects = []):
        if project_id in exclude_projects: # TODO: check if can go infinite, possibly yes
            return False

        if self.lp[(self.lp.project_id == project_id) & self.lp.finish.notnull()].shape[0] == 0: ## allocate if not allocated yet
            resource_id = [self.get_first_free_resource_id(minimal_project_start)]
            # self.allocate_time_first_free_slot(project_id, resource_id, minimal_project_start)
            self.allocate_time_continuous_per_project(project_id, resource_id, minimal_project_start)

            x = (self.av[self.av.project_id == project_id].finish - self.av[self.av.project_id == project_id].start).sum()
            y = self.lp[self.lp.project_id == project_id].worktime.iat[0]
            if y.total_seconds() != 0 and y != x:
                raise Exception("Badly allocated project: " + project_id + ", worktime: " + str(y) + ", allocated worktime: " + str(x))
        return True


    def allocate_project_and_its_predecesors(self, project_id, exclude_projects = []): # allocate predecessors in some way
        projects_in_branch = self.get_dependency_ancestors(project_id)
        projects_in_branch.add(project_id)
        # print('Projects in tree:', projects_in_branch)
        # print('Number of projects in tree:', len(projects_in_branch))

        if len(projects_in_branch) == 1: # if no predecessors then assign
            return self.allocate_project_first_fitting(project_id, self.project_start, exclude_projects)

        ## projects without any dependencies for initial round
        projects_to_allocate = self.ld[(~self.ld.predecessor_id.isin(self.ld.project_id)) & self.ld.project_id.isin(projects_in_branch)].predecessor_id.unique()


        project_allocated = False

        for p_id in projects_to_allocate:
            if self.allocate_project_first_fitting(p_id, self.project_start, exclude_projects):
                project_allocated = True

        if project_allocated == False:
            return project_allocated

        projects_to_allocate_next_iter = []

        while True:
            project_allocated = False

            projects_to_allocate = list(self.ld[self.ld.predecessor_id.isin(projects_to_allocate) & self.ld.project_id.isin(projects_in_branch)].project_id.unique()) # get successors
            projects_to_allocate = projects_to_allocate_next_iter + projects_to_allocate

            if len(projects_to_allocate) == 0:
                break

            projects_to_allocate_next_iter = []
            for p_id in projects_to_allocate:
                if self.lp[self.lp.project_id.isin(self.ld[self.ld.project_id == p_id].predecessor_id) & self.lp.finish.isnull()].shape[0] > 0:
                    projects_to_allocate_next_iter.append(p_id)
                    continue

                predecessor_finish = self.lp[self.lp.project_id.isin(self.ld[self.ld.project_id == p_id].predecessor_id)].finish.max()
                if self.allocate_project_first_fitting(p_id, predecessor_finish, exclude_projects):
                    project_allocated = True

            if project_allocated == False:
                break
                
        return project_allocated


        # print('Final number of allocated projects:', self.lp[self.lp.finish.notnull()].shape[0])
        # print()

