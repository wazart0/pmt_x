import pandas as pd





def create_availability_calendar(start_time = pd.Timestamp.now(tz='UTC'), number_of_users = 1, days_ahead = 300):
    start_time = start_time - pd.Timedelta(start_time.time().strftime('%H:%M:%S')) + pd.Timedelta(8, 'h')

    start = []
    for i in range(days_ahead):
        day = start_time + pd.Timedelta(i, 'd') 
        if day.isoweekday() != 6 and day.isoweekday() != 7:
            start.append(day)

    availability = pd.DataFrame(start, columns=['start'])
    availability['finish'] = availability.start + pd.Timedelta(8, 'h')
    availability['user_id'] = 0

    calendar = availability.copy(deep=True)
    for i in range(number_of_users-1):
        availability['user_id'] = i + 1
        calendar = pd.concat([calendar, availability])

    calendar.reset_index(inplace=True)
    calendar.drop(inplace=True, columns=['index'])

    return calendar




# class version seems to be significantly slower (or maybe not - to be confirmed)
class ProposeAssigment():

    def __init__(self, projects = None, dependencies = None, availability = None, ld = None):

        self.projects = projects
        self.dependencies = dependencies
        self.av = availability


    def initialize(self, start):
        # self.validate_schema()

        self.start = start

        self.lp = self.create_lowest_level_projects()
        self.lp['start'] = None
        self.lp['finish'] = None

        self.ld = self.create_lowest_level_dependencies()

        self.av['project_id'] = None


    # def create_wbs(self): TODO
    

    def validate_schema(self):
        self.projects.astype(dtype={'project_id': 'int64', 'parent_id': 'int64', 'worktime': 'timedelta64', 'start': 'datetime64[ns]', 'finish': 'datetime64[ns]'})
        self.dependencies.astype(dtype={'project_id': 'int64', 'predecessor_id': 'int64', 'type': 'str'})
        self.av.astype(dtype={'user_id': 'int64', 'start': 'datetime64[ns]', 'finish': 'datetime64[ns]'})


    def create_lowest_level_projects(self):
        return self.projects[~self.projects.project_id.isin(self.projects.parent_id)][['project_id', 'worktime']]
        # self.projects.worktime.loc[self.projects.project_id.isin(self.projects.parent_id)] = None
        # self.projects.drop(['worktime'], axis=1, inplace=True)


    def create_lowest_level_dependencies(self):
        projects = self.projects[self.projects.parent_id.isnull()][['project_id', 'parent_id']]
        ld = self.dependencies.copy(deep=True)

        while True:
            if projects.shape[0] == 0:
                break

            expanded_dependency = projects. \
                merge(ld, how='inner', left_on='parent_id', right_on='project_id'). \
                rename(columns={'project_id_x': 'project_id'}) \
                [ld.columns.values.tolist()]
            ld = ld[~ld.project_id.isin(projects.parent_id)].append(expanded_dependency)

            expanded_dependency = projects. \
                merge(ld, how='inner', left_on='parent_id', right_on='predecessor_id'). \
                rename(columns={'predecessor_id': 'to_remove', 'project_id_y': 'project_id', 'project_id_x': 'predecessor_id'}) \
                [ld.columns.values.tolist()]
            ld = ld[~ld.predecessor_id.isin(projects.parent_id)].append(expanded_dependency)

            projects = self.projects[self.projects.parent_id.isin(projects.project_id)][['project_id', 'parent_id']]
        
        return ld


    def update_projects(self):
        self.projects.drop(['start', 'finish', 'worktime'], axis=1, inplace=True)
        self.projects = self.projects.merge(self.lp, how='left', on='project_id')
        while True:
            tmp = self.projects.groupby('parent_id').count()
            tmp = tmp[tmp.project_id == tmp.worktime]
            update = self.projects[self.projects.parent_id.isin(tmp.index)].groupby('parent_id').agg({'worktime':'sum', 'start':'min', 'finish':'max'})

            if self.projects[self.projects.worktime.isnull()].shape[0] == 0:
                return

            for index, row in update.iterrows():
                self.projects.loc[self.projects.project_id == index, 'worktime'] = row.worktime
                self.projects.loc[self.projects.project_id == index, 'start'] = row.start
                self.projects.loc[self.projects.project_id == index, 'finish'] = row.finish


    def unassign_project_from_workers(self, project_id):
        self.av.project_id.loc[(self.av.project_id == project_id)] = None


    def assign_time_first_free(self, project_id, from_date = None, assignee = None, one_worker_per_project = False):
        lp_index = self.lp[self.lp.project_id == project_id].index[0]
        if from_date is None:
            from_date = self.av.start.min()
        if assignee is None:
            assignee = self.av.user_id.unique()
        if one_worker_per_project:
            assignee = [self.av[self.av.user_id.isin(assignee) & self.av.project_id.isnull() & (from_date <= self.av.start)].sort_values(['start']).user_id.iat[0]]
            # print(assignee)
        time_left = self.lp.at[lp_index, 'worktime']
        first = False
        for index in self.av[self.av.user_id.isin(assignee) & self.av.project_id.isnull() & (from_date <= self.av.start)].sort_values(['start']).index:
            # print('index: ', index)
            # print('start: ', self.av.at[index, 'start'])
            # print('finish: ', self.av.at[index, 'finish'])
            worktime = self.av.at[index, 'finish'] - self.av.at[index, 'start']
            self.av.at[index, 'project_id'] = self.lp.at[lp_index, 'project_id']
            if first == False:
                self.lp.at[lp_index, 'start'] = self.av.at[index, 'start']
                first = True
            # print('time_left: ', time_left)
            # print('worktime: ', worktime)
            # print('end')
            if time_left == worktime:
                self.lp.at[lp_index, 'finish'] = self.av.at[index, 'finish']
                return
            elif time_left < worktime:
                new_row = self.av.loc[index]
                new_row['project_id'] = None
                self.av.at[index, 'finish'] -= time_left
                new_row['start'] = self.av.at[index, 'finish']
                self.av.loc[self.av.shape[0]] = new_row
                self.lp.at[lp_index, 'finish'] = self.av.at[index, 'finish']
                return
            time_left -= worktime
        raise Exception("No more available time in calendar.")


    def find_incorrect_dependencies_FS(self, partial_update = False):
        update = self.ld[self.ld.type == 'FS'].merge(self.lp, left_on='predecessor_id', right_on='project_id')[['project_id_x', 'finish']].groupby(['project_id_x']).max()
        update = update.merge(self.lp, left_on='project_id_x', right_on='project_id')
        update = update[update.start < update.finish_x]
        if partial_update == True:
            update = update[update.project_id.isin(self.projects[self.projects.finish.isnull()].project_id)]
        return update



    def fix_dependence_issues(self, partial_update = False, one_worker_per_project = False):
        number_of_fixes = 0
        while True: # fix dependency issue
            update = self.find_incorrect_dependencies_FS(partial_update=partial_update)

            if update.shape[0] == 0:
                return number_of_fixes

            self.unassign_project_from_workers(update.project_id.iat[0])
            self.assign_time_first_free(update.project_id.iat[0], update.finish_x.iat[0], one_worker_per_project=one_worker_per_project)
            number_of_fixes += 1


    def create_dependency_paths(self):
        # buiself.ld dependency paths
        paths = [[i] for i in list(self.lp.project_id[~self.lp.project_id.isin(self.ld.project_id)])] # roots
        number_of_new_paths = len(paths)
        while number_of_new_paths:
            new_paths = []
            for path in paths[-number_of_new_paths:]:
                successors = list(self.ld[(self.ld.predecessor_id == path[-1])].project_id)
                for successor in successors:
                    new_path = path.copy()
                    new_path.append(successor)
                    new_paths.append(new_path)
            number_of_new_paths = len(new_paths)
            paths += new_paths
        return paths


    def assign_projects_to_resources_no_dependence(self, one_worker_per_project = False):
        for project_id in self.lp.project_id: # assign first availble time to project
            self.assign_time_first_free(project_id, one_worker_per_project=one_worker_per_project)


    def assign_projects_to_resources_first_free(self, one_worker_per_project = False):
        for project_id in self.lp.project_id: # assign first availble time to project
            self.assign_time_first_free(project_id, one_worker_per_project=one_worker_per_project)
            
        number_of_fixes = self.fix_dependence_issues(one_worker_per_project=one_worker_per_project)
        print("Preliminary assignment quality: " + str(number_of_fixes))
        return self.lp.finish.max()


    def update_lp_based_on_projects(self):
        for index, row in self.lp.iterrows(): # TODO: find better way to update
            self.lp.loc[self.lp.project_id == row['project_id'], 'start'] = self.projects[self.projects.project_id == row['project_id']].start.iloc[0]
            self.lp.loc[self.lp.project_id == row['project_id'], 'finish'] = self.projects[self.projects.project_id == row['project_id']].finish.iloc[0]


    def assign_projects_by_start_based_on_infinite_resources(self, partial_update = False, partial_update_from = None, one_worker_per_project = False):
        if partial_update == True and partial_update_from is None:
            partial_update_from = pd.Timestamp.utcnow()

        self.assign_projects_infinite_resources(partial_update=partial_update, partial_update_from=partial_update_from)
        temp_df = self.lp.copy(deep=True)
        temp_df.sort_values(['start'], inplace=True)
        self.lp.start = None
        self.lp.finish = None
        self.update_lp_based_on_projects()

        for project_id in temp_df.project_id:
            if partial_update == True:
                if self.projects[self.projects.project_id == project_id].finish.iloc[0] is pd.NaT:
                    self.assign_time_first_free(project_id, one_worker_per_project=one_worker_per_project)
            else:
                self.assign_time_first_free(project_id, one_worker_per_project=one_worker_per_project)
            
        number_of_fixes = self.fix_dependence_issues(partial_update=partial_update, one_worker_per_project=one_worker_per_project)
        print("Preliminary assignment quality: " + str(number_of_fixes))
        return self.lp.finish.max()


    def assign_projects_to_resources_from_longest_path(self, one_worker_per_project = False):

        paths = self.create_dependency_paths()

        for path in paths:
            path.append(self.lp[self.lp.project_id.isin(path)].worktime.sum())
        paths = sorted(paths, key=lambda path: path[-1], reverse=True)

        for path in paths:
            for project_id in path[:-1]:
                if self.av[(self.av.project_id == project_id)].shape[0] == 0:
                    self.assign_time_first_free(project_id, one_worker_per_project=one_worker_per_project)
                    # print('Project ' + str(project_id) + ' assigned.')
            # print(path)
            # break

        # print("Start fixing...")
            number_of_fixes = self.fix_dependence_issues(one_worker_per_project=one_worker_per_project)
            # print("Preliminary assignment quality (bigger -> worser): " + str(number_of_fixes))
        return self.lp[self.lp.end.notnull()].end.max()



    def assign_projects_to_resources_from_path_start(self, one_worker_per_project = False):
        paths = self.create_dependency_paths()
        print('Assigning projects...')
        level = 0
        while True:
            projects_on_level = list(set([(i[level] if (len(i) > level) else None) for i in paths]))
            if (len(projects_on_level) <= 1) and (projects_on_level[0] is None):
                break
            # print(projects_on_level)
            for project_id in projects_on_level:
                if (self.av[(self.av.project_id == project_id)].shape[0] == 0) and (project_id is not None):
                    self.assign_time_first_free(project_id, one_worker_per_project=one_worker_per_project)
                    # print('Project ' + str(project_id) + ' assigned.')
            level += 1

        print('Unassigned projects: ' + str(self.lp[~self.lp.project_id.isin(self.av.project_id)].shape[0]))
        # print("Start fixing...")
        number_of_fixes = self.fix_dependence_issues(one_worker_per_project=one_worker_per_project)
        print("Preliminary assignment quality (bigger -> worser): " + str(number_of_fixes))
        return self.lp.finish.max()



    def assign_projects_infinite_resources(self, partial_update = False, partial_update_from = None):
        if partial_update == True:
            if partial_update_from is None:
                partial_update_from = pd.Timestamp.utcnow()
            self.update_lp_based_on_projects()
            self.lp.start[self.lp.start.isnull()] = partial_update_from
            self.lp.finish = self.lp.apply(lambda row: (row['start'] + row['worktime']) if row['finish'] is pd.NaT else row['finish'], axis=1)
        else:
            self.lp['start'] = self.start
            self.lp['finish'] = self.lp['start'] + self.lp['worktime']

        while True:
            update = self.find_incorrect_dependencies_FS()
            # print(update)
            #1 update = update[['project_id', 'worktime', 'finish_x']].rename(columns={'finish_x': 'start'})
            #1 update['finish'] = update.start + update.worktime
            
            if update.shape[0] == 0:
                return self.lp.finish.max()

            #1 self.lp = pd.concat([self.lp[~self.lp.project_id.isin(update.project_id)], update], ignore_index=True)
            
            for index, row in update.iterrows(): # TODO: find better way to update
                self.lp.loc[self.lp.project_id == row['project_id'], 'start'] = row.finish_x
                self.lp.loc[self.lp.project_id == row['project_id'], 'finish'] = row.finish_x + row.worktime

            
        



if __name__ == "__main__":
    import time
    # TODO: parse argv and calculate


    proposal = ProposeAssigment(project_id=56, start=pd.Timestamp('2020-02-01', tz='UTC'), host='localhost', path='../../')
    algo_time_start = time()

    # finish_date = proposal.assign_projects_infinite_resources()
    # finish_date = proposal.assign_projects_infinite_resources(partial_update=True, partial_update_from=pd.Timestamp('2021-01-01', tz='UTC'))
    # finish_date = proposal.assign_projects_by_start_based_on_infinite_resources(one_worker_per_project=True)
    finish_date = proposal.assign_projects_by_start_based_on_infinite_resources(partial_update=True, partial_update_from=pd.Timestamp('2021-01-01', tz='UTC'), one_worker_per_project=True)

    # # not so good methods (probably some logic has to be reviewed):
    # finish_date = proposal.assign_projects_to_resources_first_free(one_worker_per_project=True)
    # finish_date = proposal.assign_projects_to_resources_from_longest_path(one_worker_per_project=False)
    # finish_date = proposal.assign_projects_to_resources_from_path_start(one_worker_per_project=True)

    proposal.update_projects()

    algo_time_finish = time()

    # proposal.update_projects()
    print('Project finish timestamp: ' + str(finish_date))
    print('Calculation time [s]: ' + str(algo_time_finish - algo_time_start))
    print('Unassigned workers time during project: ' + str((proposal.av[proposal.av.project_id.isnull() & (proposal.av.start <= finish_date)].finish - proposal.av[proposal.av.project_id.isnull() & (proposal.av.start <= finish_date)].start).sum()))
    # proposal.av[proposal.av.project_id.isnull() & (proposal.av.start <= finish_date)].sort_values('start')

