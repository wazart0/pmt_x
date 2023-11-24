import timeit

from src.TasksList import TasksList
from src.TasksListManager import TasksListManager


class TasksListMessages:
    def __init__(self, engine) -> None:
        # self.tasks_list = TasksList()
        self.tasks_list = TasksListManager(engine)
        pass

    def exec(self, message) -> None:
        start = timeit.timeit()

        if 'name' not in message: return f"Missing function name"

        method = None
        try:
            method = getattr(self.tasks_list, message['name'])
        except AttributeError:
            return {
                'error': f"Class `{self.tasks_list.__class__.__name__}` does not implement `{message['name']}`"
            }
            # raise NotImplementedError(f"Class `{self.tasks_list.__class__}` does not implement `{message['name']}`")

        if 'args' not in message: result = method()
        else: result = method(**message['args'])
        return {
            **result,
            'exec_time': str(timeit.timeit() - start)
        }



