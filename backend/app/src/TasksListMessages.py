import logging
import time

from src.TasksList import TasksList
from src.TasksListManager import TasksListManager

logger = logging.getLogger()

class TasksListMessages:
    def __init__(self, engine) -> None:
        # self.tasks_list = TasksList()
        self.tasks_list = TasksListManager(engine)
        pass

    def exec(self, message) -> None:
        start = time.time()

        if 'name' not in message: return { 'error': f"Missing function name" }

        method = None
        try:
            method = getattr(self.tasks_list, message['name'])
        except AttributeError:
            return {
                'error': f"Class `{self.tasks_list.__class__.__name__}` does not implement `{message['name']}`"
            }

        logger.info(message)

        if 'args' not in message: result = method()
        else: result = method(**message['args'])

        return {
            **result,
            'exec_time': time.time() - start
        }



