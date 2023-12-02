from sqlalchemy import insert, select, update, and_, or_
# from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker
import logging
import re


from src.models import _newid, User, Task, Baseline, UserView


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


    def insert(self, table, **args) -> dict:
        args['id'] = _newid()
        with self.Session() as session:
            r, = session.execute(
                insert(table).returning(table).values(**args)
            ).one()
            session.commit()
            result = r.to_dict()
        return result


    def update(self, table, id, **args) -> dict:
        with self.Session() as session:
            r, = session.execute(
                update(table).returning(table).values(**args).where(table.id==id)
            ).one()
            session.commit()
            result = r.to_dict()
        return result


    def upsert(self, table, **args) -> dict:
        if 'id' in args: return self.update(table, **args)
        return  self.insert(table, **args)


    def upsert_view(self, **args) -> dict:
        return { 'type': 'views', 'data': self.upsert(UserView, **args) }


    def upsert_task(self, **args) -> dict:
        return { 'type': 'tasks', 'data': self.upsert(Task, **args) }


    def upsert_baseline(self, **args) -> dict:
        return { 'type': 'baselines', 'data': self.upsert(Baseline, **args) }

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
    


    def get_users(self):
        result = {}
        with self.Session() as session:
            for r, in session.execute(select(User)):
                result[str(r.id)] = { 'username': r.name }
        return { 'type': 'userList', 'data': result }
    

    
    def get_views(self, user_id):
        result = {}
        with self.Session() as session:
            for id, name, in session.execute(
                select(UserView.id, UserView.name).where(UserView.user_id == user_id)
            ):
                result[str(id)] = name

        return { 'type': 'userViewList', 'data': result }


    def get_dashboard(self, user_id, view_id):
        result = {
            'tasks': {},
            'baselines': {},
            'userView': {}
        }
        with self.Session() as session:

            if view_id is not None: user_view = session.get(UserView, view_id)
            else: user_view = session.execute(select(UserView).where(and_(UserView.user_id == user_id, UserView.name == 'default'))).first()
            if user_view is None: return { 'error': f'View `{view_id}` doesn`t exist'}
            result['userView'] = user_view.to_dict()

            if result['userView']['filter'] in [None, '']:
                for r, in session.execute(select(Task)): # TODO: implement pagination
                    result['tasks'].update({str(r.id): r.to_dict()})
                return { 'type': 'dashboard', 'data': result }
            
            baseline_regex = r'''baseline\s*\[\s*((~?(\"|')[ a-zA-Z0-9]+(\"|')|[a-zA-Z0-9]+)\s*,\s*)*(~?(\"|')[ a-zA-Z0-9]+(\"|')|[a-zA-Z0-9]+)\s*\]'''
            task_regex = r'''task\s*\[\s*((~?(\"|')[ a-zA-Z0-9]+(\"|')|[a-zA-Z0-9]+)\s*,\s*)*(~?(\"|')[ a-zA-Z0-9]+(\"|')|[a-zA-Z0-9]+)\s*\]'''
            # or_regex = r''' or '''

            baseline_match = re.search(baseline_regex, result['userView']['filter'])
            task_match = re.search(task_regex, result['userView']['filter'])
            logger.debug(baseline_match)
            logger.debug(task_match)
            # logger.debug(str(task_match))

            if task_match:
                params = r'''\[\s*((~?(\"|')[ a-zA-Z0-9]+(\"|')|[a-zA-Z0-9]+)\s*,\s*)*(~?(\"|')[ a-zA-Z0-9]+(\"|')|[a-zA-Z0-9]+)\s*\]'''
                task_match = re.search(params, task_match.group())
                logger.debug(task_match)
                params = r'''~?(\"|')[ a-zA-Z0-9]+(\"|')|[a-zA-Z0-9]+'''
                tasks_inputs = re.search(params, task_match.group())
                logger.debug(tasks_inputs)
                

        return { 'type': 'dashboard', 'data': result }



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

