from dataclasses import dataclass
from typing import Dict, Generator, ItemsView, List
import json
from json import JSONDecodeError
from collections import defaultdict
from contextlib import contextmanager

from exceptions import IdNotFoundException

@dataclass
class Task:
    """
    Датакласс задача

    Attributes:
        id: Идентификатор
        name: название
        description: описание
        category: категория
        deadline: срок выполнения
        priority: приоритет
        status: "выполнена" или "не выполнена"

    """

    name: str
    description: str
    category: str
    deadline: str
    priority: str
    id: int | None = None
    status: str = "Not complete"


class TaskManager:
    """ Класс Менеджер задач."""

    STATUS_COMPLETE = "Complete"
    STATUS_NOT_COMPLETE = "Not complete"


    def __init__(self) -> None:
        """Инициализация класса."""
        self.data_tasks: Dict[int, dict] = dict()
        self.index: TaskIndex = TaskIndex()

        try:
            with open('data.json', 'r') as f:
                self.data_tasks = {int(key): value for key, value in json.load(f).items()}
                self.index.load_from_file()
        except FileNotFoundError:
            # Замалчиваем, потому что штатная ситуация при первом запуске приложения.
            pass
        except JSONDecodeError:
            print('Нечитаемый формат файла.')


    def add_task(self, task: Task) -> None:
        """ Добавляет задачу. Присваивает задаче id, обновляет индекс."""
        if not self.data_tasks:
            task.id = 1
        else:
            task.id = max(self.data_tasks.keys()) + 1
        self.data_tasks[task.id]: Dict[int, dict] = {'name': task.name, 'description': task.description,
                                                     'category': task.category, 'deadline': task.deadline,
                                                     'priority': task.priority,
                                                     'status': task.status}
        self.index.update(task)


    def delete_task(self, id: int) -> None:
        """ Удаляет задачу из менеджера. Обновляет индекс."""
        try:
            self.data_tasks[id]
        except KeyError:
            raise IdNotFoundException
        category = self.data_tasks[id]['category']
        status = self.data_tasks[id]['status']
        self.data_tasks.pop(id)
        self.index.delete(id, category, status)


    def delete_tasks_by_category(self, category):
        """Удаляет категория задач из менеджера. Обновляет индекс."""
        try:
            ids = self.index.data['data_category'][category]
        except KeyError:
            raise KeyError
        for id in ids:
            self.data_tasks.pop(id)
        self.index.delete_category(ids, category)


    def search_task(self, field: str, value: str):
        """Поиск задачи по ключевому слову, статусу или категории."""
        result = list()
        if field == 'key_word':
            for key, task in self.data_tasks.items():
                for data in task.values():
                    if value in data:
                        result.append((key, task))
                        break
        else:
            ids = self.index.search(field, value)
            for id in ids:
                result.append((id, self.data_tasks[id]))
        return result



    def change_data(self, id: int, field: str, value: str) -> None:
        """Изменяет поле задачи."""
        try:
            self.data_tasks[id]
        except KeyError:
            raise IdNotFoundException

        try:
            self.data_tasks[id][field]
        except KeyError:
            raise KeyError

        if field == 'category':
            self.index.change_category(id, value, self.data_tasks[id]['category'])

        self.data_tasks[id][field] = value


    def change_status(self, id: int) -> None:
        """Изменение статуса задачи с "not complete" на "Complete"."""
        try:
            task = self.data_tasks[id]
        except KeyError:
            raise IdNotFoundException
        if task['status'] == self.STATUS_NOT_COMPLETE:
            task['status'] = self.STATUS_COMPLETE
            self.index.change_status(id)


    def show_tasks(self) -> ItemsView[int, dict]:
        """ Возвращает пары id задача."""
        return self.data_tasks.items()


    def show_tasks_by_category(self, category: str) -> List:
        """Возвращает пары id задача по категории."""
        try:
            data_category = self.index.data['data_category'][category]
        except KeyError:
            raise KeyError
        result = list()
        for id in data_category:
            result.append((id, self.data_tasks[id]))
        return result


    def close(self) -> None:
        """Сохраняет данные в JSON-файл."""
        with open('data.json', 'w') as f:
            json.dump(self.data_tasks, f)
        self.index.close()


    @contextmanager
    def lock(self) -> Generator["TaskManager", None, None]:
        """Контекстный менеджер."""
        try:
            yield self
        finally:
            self.close()


class TaskIndex:
    """Класс индексации задач."""

    data: Dict[str, Dict[str | int, set[int]]] = defaultdict(dict)
    search_type: Dict[str, dict] = defaultdict(dict)

    def load_from_file(self) -> None:
        """ Десериализует данные."""
        try:
            with open('index.json', 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, JSONDecodeError):
            return
        self.data['data_status'] = {key: set(value) for key, value in
                                    data['data_status'].items()}
        self.data['data_category'] = {key: set(value) for key, value in
                                  data['data_category'].items()}


    def change_category(self, id: int, new_category: str, old_category: str) -> None:
        """Обновляет индекс категории."""
        self.data['data_category'][old_category].remove(id)
        try:
            self.data['data_category'][new_category].add(id)
        except KeyError:
            self.data['data_category'][new_category] = {id}


    def change_status(self, id: int) -> None:
        """Обновляет индекс статуса."""
        self.data['data_status']['Not complete'].remove(id)
        try:
            self.data['data_status']['Complete'].add(id)
        except KeyError:
            self.data['data_status']['Complete'] = {id}


    def update(self, task: Task) -> None:
        """ Обновляет индекс под новую задачу."""
        data_type = [self.data['data_status'], self.data['data_category']]
        data_book = [task.status, task.category]
        for data, key in zip(data_type, data_book):
            try:
                data[key].add(task.id)
            except KeyError:
                data[key] = {task.id}


    def delete(self, id: int, category: str, status: str) -> None:
        """Удаляет данные из индекса."""
        self.data['data_category'][category].remove(id)
        self.data['data_status'][status].remove(id)


    def delete_category(self, ids: set[int], category: str) -> None:
        """Удаляет категорию из индекса."""
        self.data['data_category'][category] -= ids
        for status in self.data['data_status']:
            status -= ids


    def search(self, field: str, value: str | int) -> set[int]:
        """Поиск по индексу."""
        if field == 'category':
            data = self.data['data_category']
        else:
            data = self.data['data_status']
        try:
            return data[value]
        except KeyError:
            return set()


    def close(self) -> None:
        """Сериализует данные."""
        with open('index.json', 'w') as f:
            data = dict()
            data['data_status'] = {key: list(value) for key, value in self.data['data_status'].items()}
            data['data_category'] = {key: list(value) for key, value in self.data['data_category'].items()}
            json.dump(data, f)
