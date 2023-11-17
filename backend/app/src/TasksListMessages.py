from src.TasksList import TasksList


class TasksListMessages:
    def __init__(self) -> None:
        self.tasks_list = TasksList()
        pass

    def exec(self, message) -> None:
        if 'name' not in message: return f"Missing function name"

        method = None
        try:
            method = getattr(self.tasks_list, message['name'])
        except AttributeError:
            return f"Class `{self.tasks_list.__class__}` does not implement `{message['name']}`"
            # raise NotImplementedError(f"Class `{self.tasks_list.__class__}` does not implement `{message['name']}`")

        if 'args' not in message: method()
        else: method(**message['args'])

        return 0


