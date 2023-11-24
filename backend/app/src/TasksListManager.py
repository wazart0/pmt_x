import functools
from sqlalchemy import select, insert, inspect, and_
from sqlalchemy.orm import sessionmaker
import logging
import uuid

from src.models import Task, Baseline, UserView


logger = logging.getLogger()



class TasksListManager(object):
    def __init__(self, engine) -> None:
        self.engine = engine
        self.Session = sessionmaker(engine)

    # def reinit_tasks(self, tasks) -> None:
    #     self.tasks = tasks
        # self.recreate_id2index_map()


    # def index(self, task_id) -> int:
    #     for index in range(len(self.tasks)): 
    #         if task_id == self.tasks[index]['id']: return index
    #     return None
    


    def get_users(self):
        result = {}
        with self.Session() as session:
            for r, in session.execute(
                select(UserView.user_id)
            ):
                result[str(r)] = { 'username': 'xxx' }

        return { 'type': 'userList', 'data': result }

    
    
    def add_view(self, user_id, view_name = 'default', doc = { 'filter': None }):
        with self.Session() as session:
            user_view = UserView(
                id = uuid.uuid4(),
                user_id = user_id,
                name = view_name,
                doc = doc         
            )
            session.add(user_view)
            session.commit()
            
        return { 'type': None }
    

    
    def get_views(self, user_id):
        result = {}
        with self.Session() as session:
            for id, name, in session.execute(
                select(UserView.id, UserView.name).where(UserView.user_id == user_id)
            ):
                result[str(id)] = { 'name': name }

        return { 'type': 'userViewList', 'data': result }



    def get_dashboard(self, user_id, view_id):
        result = {
            'tasks': {},
            'baseline': {},
            'baselines': {},
            'userView': {}
        }
        with self.Session() as session:

            if view_id is not None: user_view = session.get(UserView, view_id)
            else: user_view = session.execute(select(UserView).where(and_(UserView.user_id == user_id, UserView.name == 'default'))).first()
            if user_view is None: return { 'error': f'View `{view_id}` doesn`t exist'}
            result['userView'] = user_view.to_dict()

            if not result['userView'][view_id]['doc'] or \
                result['userView'][view_id]['doc']['filter'] in [None, '']:
                for r, in session.execute(select(Task)): # TODO: implement pagination
                    result['tasks'].update(r.to_dict())
            else:
                pass

        return { 'type': 'dashboard', 'data': result }



    def add_task(self, name) -> None:
        with self.Session() as session:
            task = Task(
                id = uuid.uuid4(),
                name = name,
                doc = {}
            )
            session.add(task)
            session.commit()
            result = task.to_dict()
        
        logger.debug(result)
        return { 'type': 'tasks', 'data': result }

        # self.tasks.append({
        #     'id': len(self.tasks),
        #     'name': name,
        #     'description': None,
        #     'baselines': [],

        #     'wbs': None,
        #     'worktime': None,
        #     'start': None,
        #     'finish': None,
        #     'parent': None,

        #     'hidden': False,
        #     'hasChildren': False,
        #     'hiddenChildren': False
        # })
        # self.recreate_id2index_map()



    # def update_task_name(self, task_id, name):
    #     self.tasks[self.index(task_id)]['name'] = name


    # def add_task_to_baseline(self, task_id, baseline_id = None) -> None:
    #     no_of_siblings = 1
    #     for task in self.tasks:
    #         if task['parent'] is None and task['wbs'] is not None:
    #             no_of_siblings += 1

    #     self.tasks[self.index(task_id)]['wbs'] = str(no_of_siblings)
    #     # self.recreate_id2index_map()


    # def hide_subtree(self, task_id) -> None: # assumption is that the data is sorted by ID/WBS, means parent is always before child in array
    #     subtree = [task_id]
    #     self.tasks[self.index(task_id)]['hiddenChildren'] = True
    #     for task in self.tasks:
    #         if task['parent'] not in subtree: continue
    #         if task['hasChildren']: subtree.append(task['id'])
    #         task['hidden'] = True


    # def show_subtree(self, task_id) -> None: # assumption is that the data is sorted by ID/WBS, means parent is always before child in array
    #     subtree = [task_id]
    #     children_kept_hidden = []
    #     self.tasks[self.index(task_id)]['hiddenChildren'] = False
    #     for task in self.tasks:
    #         if task['parent'] not in subtree: continue
    #         if task['hasChildren']: subtree.append(task['id'])
    #         if (task['parent'] in children_kept_hidden or task['hiddenChildren'] == True) and task['hasChildren']:
    #             children_kept_hidden.append(task['id'])
    #         if task['parent'] not in children_kept_hidden: task['hidden'] = False


    # def sort_by_wbs(self) -> None:
    #     def compare(a, b) -> int:
    #         if a['wbs'] == b['wbs']: return 0
    #         if a['wbs'] == None: return 1
    #         if b['wbs'] == None: return -1
    #         a_array = a['wbs'].split('.')
    #         b_array = b['wbs'].split('.')
    #         for i in range(len(a_array) if len(a_array) < len(b_array) else len(b_array)):
    #             if int(a_array[i]) < int(b_array[i]): return -1
    #             if int(a_array[i]) > int(b_array[i]): return 1
    #         return 0
    #     self.tasks.sort(key=functools.cmp_to_key(compare))
    #     # self.recreate_id2index_map()


    # def recreate_id2index_map(self) -> None:
    #     index = 0
    #     self.id2index_map = {}
    #     for task in self.tasks: 
    #         self.id2index_map[task['id']] = index
    #         index += 1

