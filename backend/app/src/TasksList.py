import functools



class TasksList(object):

    def reinit_tasks(self, tasks) -> None:
        self.tasks = tasks
        # self.recreate_id2index_map()


    def index(self, task_id) -> int:
        for index in range(len(self.tasks)): 
            if task_id == self.tasks[index]['id']: return index
        return None
    

    def get_tasks(self):
        return self.tasks


    def add_task(self, name) -> None:
        self.tasks.append({
            'id': len(self.tasks),
            'name': name,
            'description': None,
            'baselines': [],

            'wbs': None,
            'worktime': None,
            'start': None,
            'finish': None,
            'parent': None,

            'hidden': False,
            'hasChildren': False,
            'hiddenChildren': False
        })
        # self.recreate_id2index_map()


    def update_task_name(self, task_id, name):
        self.tasks[self.index(task_id)]['name'] = name


    def add_task_to_baseline(self, task_id, baseline_id = None) -> None:
        no_of_siblings = 1
        for task in self.tasks:
            if task['parent'] is None and task['wbs'] is not None:
                no_of_siblings += 1

        self.tasks[self.index(task_id)]['wbs'] = str(no_of_siblings)
        # self.recreate_id2index_map()


    def hide_subtree(self, task_id) -> None: # assumption is that the data is sorted by ID/WBS, means parent is always before child in array
        subtree = [task_id]
        self.tasks[self.index(task_id)]['hiddenChildren'] = True
        for task in self.tasks:
            if task['parent'] not in subtree: continue
            if task['hasChildren']: subtree.append(task['id'])
            task['hidden'] = True


    def show_subtree(self, task_id) -> None: # assumption is that the data is sorted by ID/WBS, means parent is always before child in array
        subtree = [task_id]
        children_kept_hidden = []
        self.tasks[self.index(task_id)]['hiddenChildren'] = False
        for task in self.tasks:
            if task['parent'] not in subtree: continue
            if task['hasChildren']: subtree.append(task['id'])
            if (task['parent'] in children_kept_hidden or task['hiddenChildren'] == True) and task['hasChildren']:
                children_kept_hidden.append(task['id'])
            if task['parent'] not in children_kept_hidden: task['hidden'] = False


    def sort_by_wbs(self) -> None:
        def compare(a, b) -> int:
            if a['wbs'] == b['wbs']: return 0
            if a['wbs'] == None: return 1
            if b['wbs'] == None: return -1
            a_array = a['wbs'].split('.')
            b_array = b['wbs'].split('.')
            for i in range(len(a_array) if len(a_array) < len(b_array) else len(b_array)):
                if int(a_array[i]) < int(b_array[i]): return -1
                if int(a_array[i]) > int(b_array[i]): return 1
            return 0
        self.tasks.sort(key=functools.cmp_to_key(compare))
        # self.recreate_id2index_map()


    def recreate_id2index_map(self) -> None:
        index = 0
        self.id2index_map = {}
        for task in self.tasks: 
            self.id2index_map[task['id']] = index
            index += 1

