import functools



class TasksList(object):

    def reinit_tasks(self, tasks) -> None:
        self.tasks = tasks
        # self.recreate_id2index_map()


    def index(self, task_id) -> int:
        for index in range(len(self.tasks)): 
            if task_id == self.tasks[index]['id']: return index


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


    def add_task_to_baseline(self, task_id, baseline_id = None) -> None:
        no_of_siblings = 1
        for task in self.tasks:
            if task['parent'] is None and task['wbs'] is not None:
                no_of_siblings += 1

        self.tasks[self.index(task_id)]['wbs'] = str(no_of_siblings)
        # self.recreate_id2index_map()


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