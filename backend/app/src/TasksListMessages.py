from src.TasksList import TasksList


class TasksListMessages:
    def __init__(self) -> None:
        self.tasks_list = TasksList()
        pass

    def exec(self, message) -> None:
        if 'name' not in message: return
        match message['name']:
            case 'addTask':
                self.tasks_list.add_task(message['metadata']['taskName'])
                pass

            case 'addTaskToBaseline':
                self.tasks_list.add_task_to_baseline(message['metadata']['taskId'])

            case _:
                pass

    
