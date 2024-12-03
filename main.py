import sys

from actions import action_dispatcher
from task_manager import TaskManager


def main():
    task_manager = TaskManager()
    with task_manager.lock():
        while (action:= input('Введите команду для работы: ')) != "exit":
            if action in action_dispatcher:
                action_dispatcher[action](task_manager)
            else:
                print('Команда не распознана.')


if __name__ == "__main__":
    sys.exit(main())