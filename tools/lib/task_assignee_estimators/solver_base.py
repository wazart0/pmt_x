#%%
import pandas as pd





class SolverBase():

    def __init__(self, projects = None, dependencies = None):

        self.projects = projects
        self.dependencies = dependencies

        # self.partial_update = False
        # self.partial_update_from = pd.Timestamp.utcnow()

        self.project_start = pd.Timestamp.utcnow()
        

    def config(self, **kwargs):
        if 'project_start' in kwargs:
            self.project_start = kwargs['project_start']
        # if 'partial_update' in parameters:
        #     self.partial_update = parameters['partial_update']
        # if 'partial_update_from' in parameters:
        #     self.partial_update_from = parameters['partial_update_from']


    def initialize(self):
        # self.validate_schema()
        self.lp = self.create_lowest_level_projects()
        self.ld = self.create_lowest_level_dependencies()


    def create_wbs(self): # TODO finish
        self.projects['wbs'] = (self.projects.groupby(['parent_id']).cumcount() + 1).astype(str)
        
        projects_to_update = self.projects[self.projects.parent_id.isnull()].project_id
        while True:
            projects_to_update = self.projects[self.projects.parent_id.isin(projects_to_update)].project_id

            if projects_to_update.shape[0] == 0:
                return
            
            self.projects = self.projects.merge(self.projects[['wbs', 'project_id']], how='left', left_on='parent_id', right_on='project_id')
            self.projects['wbs'] = self.projects.apply(lambda row: row['wbs_y'] + '.' + row['wbs_x'] if row['project_id_x'] in projects_to_update.to_list() else row['wbs_x'], axis=1)
            self.projects.drop(inplace=True, columns=['wbs_x', 'wbs_y', 'project_id_y'])
            self.projects.rename(inplace=True, columns={"project_id_x": "project_id"})
    

    def validate_schema(self):
        self.projects.astype(dtype={'project_id': 'int64', 'parent_id': 'int64', 'worktime': 'timedelta64', 'start': 'datetime64[ns]', 'finish': 'datetime64[ns]'})
        self.dependencies.astype(dtype={'project_id': 'int64', 'predecessor_id': 'int64', 'type': 'str'})


    def create_lowest_level_projects(self):
        # if self.partial_update:
        #     return self.projects[~self.projects.project_id.isin(self.projects.parent_id)][['project_id', 'worktime', 'start', 'finish']]
        return self.projects[~self.projects.project_id.isin(self.projects.parent_id)].copy(deep=True)
        

    def create_lowest_level_dependencies(self):
        if not self.dependencies:
            return None

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


    def update_projects(self, from_lp = True):
        if from_lp:
            self.projects.drop(['start', 'finish', 'worktime'], axis=1, inplace=True)
            self.projects = self.projects.merge(self.lp[['project_id', 'start', 'finish', 'worktime']], how='left', on='project_id')

        # while True:
        #     tmp = self.projects.groupby('parent_id').count()
        #     tmp = tmp[tmp.project_id == tmp.worktime]
        #     update = self.projects[self.projects.parent_id.isin(tmp.index)].groupby('parent_id').agg({'worktime':'sum', 'start':'min', 'finish':'max'})

        #     if self.projects[self.projects.worktime.isnull()].shape[0] == 0:
        #         return

        #     for index, row in update.iterrows():
        #         self.projects.loc[self.projects.project_id == index, 'worktime'] = row.worktime
        #         self.projects.loc[self.projects.project_id == index, 'start'] = row.start
        #         self.projects.loc[self.projects.project_id == index, 'finish'] = row.finish

        parents = self.projects[~self.projects.project_id.isin(self.projects.parent_id)].project_id.copy(deep=True) # lowest level projects (init)

        while True:
            parents = self.projects[self.projects.parent_id.isin(parents)].project_id.copy(deep=True)

            if len(parents) == 0:
                return

            for parent_id in parents:
                self.projects.loc[self.projects.project_id == parent_id, 'worktime'] = self.projects[(self.projects.project_id == parent_id) & self.projects.worktime.notnull()].worktime.sum()
                self.projects.loc[self.projects.project_id == parent_id, 'start'] = self.projects[(self.projects.project_id == parent_id) & self.projects.start.notnull()].start.min()
                self.projects.loc[self.projects.project_id == parent_id, 'finish'] = self.projects[(self.projects.project_id == parent_id) & self.projects.finish.notnull()].finish.max()


    # def find_incorrect_dependencies_FS(self):
    #     update = self.ld[self.ld.type == 'FS'].merge(self.lp, left_on='predecessor_id', right_on='project_id')[['project_id_x', 'finish']].groupby(['project_id_x']).max()
    #     update = update.merge(self.lp, left_on='project_id_x', right_on='project_id')
    #     update = update[update.start < update.finish_x]
    #     # if partial_update == True:
    #     #     update = update[update.project_id.isin(self.projects[self.projects.finish.isnull()].project_id)]
    #     return update

    
    def find_incorrectly_allocated_projects_FS(self):
        update = self.ld[self.ld.type == 'FS'].merge(self.lp, left_on='predecessor_id', right_on='project_id')[['project_id_x', 'predecessor_id', 'type', 'start', 'finish']]
        update.rename(inplace=True, columns={
            "project_id_x": "project_id",
            "worktime": "predecessor_worktime",
            "start": "predecessor_start",
            "finish": "predecessor_finish"
        })
        update = update.merge(self.lp, on='project_id')
        update.rename(inplace=True, columns={
            "worktime": "project_worktime",
            "start": "project_start",
            "finish": "project_finish"
        })
        return update[update.project_start < update.predecessor_finish]


    def find_circular_dependencies(self):
        traces = []
        
        def traverse_through_dependencies(self, trace):
            for predecessor in self.ld[self.ld.project_id == trace[-1]].predecessor_id:
                tmp_list = trace + [predecessor]
                if len(set(tmp_list)) != len(tmp_list):
                    print('Circular dependency detected: ', tmp_list)
                    traces.append(tmp_list)
                    continue
                traverse_through_dependencies(self, tmp_list)
        for _, row in self.ld.iterrows():
            traverse_through_dependencies(self, [row['project_id'], row['predecessor_id']])

        return traces


    def allocate_projects_infinite_resources(self):
        self.lp['start'] = self.project_start
        self.lp['finish'] = self.lp.start + self.lp.worktime

        while True:
            update = self.find_incorrectly_allocated_projects_FS()
            
            if update.shape[0] == 0:
                return self.lp.start.min(), self.lp.finish.max()
            
            for _, row in update.iterrows(): # TODO: find better way to update
                self.lp.loc[self.lp.project_id == row['project_id'], 'start'] = row.predecessor_finish
                self.lp.loc[self.lp.project_id == row['project_id'], 'finish'] = row.predecessor_finish + row.project_worktime


    def get_cpm(self, exclude = []):
        cpm = []
        
        def traverse_through_dependencies(self, trace, start):
            # modify (self.lp.finish == start) from equals to closest available
            predecessors = self.ld[self.ld.project_id == trace[-1]].predecessor_id
            for predecessor in self.lp[self.lp.project_id.isin(predecessors) & (self.lp.finish == start)].project_id:
                traverse_through_dependencies(self, trace + [predecessor], self.lp[self.lp.project_id == predecessor].start.max())
                if self.lp.start.min() == self.lp[self.lp.project_id == predecessor].start.min():
                    cpm.append(trace + [predecessor])

        projects = self.lp[~self.lp.project_id.isin(exclude)]
        for project_id in projects[projects.finish == projects.finish.max()].project_id:
            traverse_through_dependencies(self, [project_id], projects[projects.project_id == project_id].start.max())

        return cpm





class SolverBaseResources(SolverBase):
    
    def __init__(self, projects = None, dependencies = None, availability = None):
        super().__init__(projects, dependencies)
        self.av = availability


    def validate_schema(self):
        super().validate_schema()
        self.av.astype(dtype={'resource_id': 'int64', 'start': 'datetime64[ns]', 'finish': 'datetime64[ns]'})


    def deallocate_project_from_resources(self, project_id):
        self.av.project_id.loc[(self.av.project_id == project_id)] = None


    def allocate_time_first_free_slot(self, project_id: str, resources_ids: list, from_date: pd.Timestamp):
        lp_index = self.lp[self.lp.project_id == project_id].index[0]

        time_left = self.lp.at[lp_index, 'worktime']
        first = True
        for index in self.av[self.av.resource_id.isin(resources_ids) & self.av.project_id.isnull() & (from_date <= self.av.start)].sort_values(['start']).index:
            if time_left == pd.Timedelta(0, 's') and first:
                self.lp.at[lp_index, 'start'] = self.av.at[index, 'start']
                self.lp.at[lp_index, 'finish'] = self.av.at[index, 'start']
                return

            worktime = self.av.at[index, 'finish'] - self.av.at[index, 'start']

            self.av.at[index, 'project_id'] = self.lp.at[lp_index, 'project_id']

            if first:
                self.lp.at[lp_index, 'start'] = self.av.at[index, 'start']
                first = False

            if time_left == worktime:
                self.lp.at[lp_index, 'finish'] = self.av.at[index, 'finish']
                return
            elif time_left < worktime:
                new_row = self.av.loc[index].copy(deep=True)
                new_row['project_id'] = None
                self.av.at[index, 'finish'] = self.av.at[index, 'start'] + time_left
                new_row['start'] = self.av.at[index, 'finish']
                self.av.loc[self.av.shape[0]] = new_row
                self.lp.at[lp_index, 'finish'] = self.av.at[index, 'finish']
                return

            time_left -= worktime

        self.lp.at[lp_index, 'start'] = None
        self.lp.at[lp_index, 'finish'] = None
        self.deallocate_project_from_resources(project_id)
        raise Exception("No more available time in calendar.")


    def allocate_time_continuous_per_project(self, project_id: str, resources_ids: list, from_date: pd.Timestamp):
        lp_index = self.lp[self.lp.project_id == project_id].index[0]

        time_left = self.lp.at[lp_index, 'worktime']
        first = False
        for index in self.av[self.av.resource_id.isin(resources_ids) & (from_date <= self.av.start)].sort_values(['start']).index:
            if time_left == pd.Timedelta(0, 's') and first:
                self.lp.at[lp_index, 'start'] = self.av.at[index, 'start']
                self.lp.at[lp_index, 'finish'] = self.av.at[index, 'start']
                return
            
            if self.av.at[index, 'project_id'] is not None:
                time_left = self.lp.at[lp_index, 'worktime']
                first = False
                self.av.loc[self.av.project_id == self.lp.at[lp_index, 'project_id'], 'project_id'] = None
                continue

            worktime = self.av.at[index, 'finish'] - self.av.at[index, 'start']

            self.av.at[index, 'project_id'] = self.lp.at[lp_index, 'project_id']

            if first == False:
                self.lp.at[lp_index, 'start'] = self.av.at[index, 'start']
                first = True

            if time_left == worktime:
                self.lp.at[lp_index, 'finish'] = self.av.at[index, 'finish']
                return
            elif time_left < worktime:
                new_row = self.av.loc[index].copy(deep=True)
                new_row['project_id'] = None
                self.av.at[index, 'finish'] = self.av.at[index, 'start'] + time_left
                new_row['start'] = self.av.at[index, 'finish']
                self.av.loc[self.av.shape[0]] = new_row
                self.lp.at[lp_index, 'finish'] = self.av.at[index, 'finish']
                return

            time_left -= worktime

        self.lp.at[lp_index, 'start'] = None
        self.lp.at[lp_index, 'finish'] = None
        self.deallocate_project_from_resources(project_id)
        raise Exception("No more available time in calendar.")


    def get_first_free_resource_id(self, from_date: pd.Timestamp):
        # return self.av[self.av.project_id.isnull() & (self.av.start == self.av[self.av.project_id.isnull()].start.min())].resource_id.iat[0]
        return self.av[self.av.project_id.isnull() & (from_date <= self.av.start)].sort_values(['start']).resource_id.iat[0]


    @staticmethod
    def merge_calendars(main, availibility):
        if main.shape[0] == 0:
            return availibility

        out = main.copy(deep=True)

        for _, row_av in availibility.iterrows():
            related = main[(main.resource_id == row_av['resource_id']) & (main.start <= row_av['finish']) & (main.finish >= row_av['start'])]
            if related.shape[0]:
                if related.shape[0] == 1 and \
                    row_av['start'] == related.start.min() and \
                    row_av['finish'] == related.finish.max():
                        continue
                # for _, row_rel in related.sort_values('start').iterrows(): # TODO: serve more advanced scenarios
                #     pass
                if related.finish.max() < row_av['finish']:
                    row_av['start'] = related.finish.max()
                    out.loc[out.shape[0]] = row_av.copy(deep=True)
                else:
                    print("problem in calendar merge")
            else:
                out.loc[out.shape[0]] = row_av.copy(deep=True)

        return out


    @staticmethod
    def create_availability_calendar(start_time = pd.Timestamp.now(tz='UTC'), number_of_users = 1, days_ahead = 300):
        # start_time = start_time - pd.Timedelta(start_time.time().strftime('%H:%M:%S')) + pd.Timedelta(8, 'h')
        start_time = start_time.normalize() + pd.Timedelta(8, 'h')
        # start_time.microsecond = 0
        # start_time.nanosecond = 0

        start = []
        for i in range(days_ahead):
            day = start_time + pd.Timedelta(i, 'd') 
            if day.isoweekday() != 6 and day.isoweekday() != 7:
                start.append(day)

        availability = pd.DataFrame(start, columns=['start'])
        availability['finish'] = availability.start + pd.Timedelta(8, 'h')
        availability['resource_id'] = 0

        calendar = availability.copy(deep=True)
        for i in range(number_of_users-1):
            availability['resource_id'] = i + 1
            calendar = pd.concat([calendar, availability])

        calendar.reset_index(inplace=True)
        calendar.drop(inplace=True, columns=['index'])

        return calendar
