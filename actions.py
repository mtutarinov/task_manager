from task_manager import Task, TaskManager
from exceptions import NullValueException, NotValidPriorityException, IdNotFoundException
from datetime import datetime


def _check_empty_field(value: str) -> str:
    """Проверяет значение поля."""
    if not value:
        print('Поле обязательно для заполнения.')
        raise NullValueException
    return value


def _check_category(value: str) -> str:
    category = {
        'Дом': 'home',
        'Работа': 'work',
        'Учеба': 'study',
        'Личное': 'personal'
    }
    try:
        return category[value]
    except KeyError:
        raise KeyError


def add_task(task_manager: TaskManager) -> None:
    """Добавляет задачу."""
    try:
        name = _check_empty_field(input('Введите название задачи: '))
    except NullValueException:
        return
    description = input('Введите описание задачи: ')
    try:
        category = _check_category(input('Введите категорию задачи: '))
    except KeyError:
        print('Не существующая категория')
        return
    deadline = input('формат даты: Год. Месяц. День Введите дату выполнения: ')
    try:
        datetime.strptime(deadline, '%Y.%m.%d')
    except ValueError:
        print('Не правильный формат даты.')
        return
    priority = input('В приоритете допустимы следующие значения: low, middle, high. Введите приоритет задачи.')
    if priority not in ('low', 'middle', 'high'):
        print(NotValidPriorityException(priority))
        return
    task = Task(name, description, category, deadline, priority)
    task_manager.add_task(task)
    print(f'Задача успешно добавлена. Ее id {task.id}.')


def delete_task(task_manager: TaskManager):
    """Удаляет задачу из мененджера."""
    try:
        id = int(input('Введите id задачи, которую хотите удалить: '))
    except ValueError:
        print('Не является числом.')
        return
    try:
        task_manager.delete_task(id)
    except IdNotFoundException:
        print('Задача не найдена.')
        return
    print('задача удалена.')


def delete_tasks_by_category(task_manager: TaskManager):
    """Удаляет категорию задач из менеджера."""
    category = input('Введите название категории: ')
    try:
        task_manager.show_tasks_by_category(category)
    except KeyError:
        print('Категория не найдена.')
        return
    print('Категория удалена.')


def search_task(task_manager: TaskManager):
    """Поиск задачи по ключевому слову, категории или статусу."""
    field = input('Введите тип поля по которому хотите найти задачу: ')
    if field not in ('key_word', 'status', 'category'):
        print('Неправильный тип поля для поиска')
        return
    value = input('Введите введите значение: ')
    result = task_manager.search_task(field, value)
    for id, data in result:
        print(
            f"id: {id} Название: {data['name']} Описание: {data['description']} Категория: {data['category']} Выполнить: {data['deadline']} Приоритет: {data['priority']} Статус: {data['status']}")


def change_task_status(task_manager: TaskManager):
    """Изменяет статус задачи."""
    id = input('Введите id книги: ')
    try:
        id = int(id)
    except ValueError:
        print(f'{id}: Не является числом.')
        return
    try:
        task_manager.change_status(id)
    except IdNotFoundException as e:
        print(e)
        return
    print('Статус изменен.')


def change_task_field(task_manager: TaskManager):
    """Изменяет поле задачи."""
    id = input('Введите id книги: ')
    try:
        id = int(id)
    except ValueError:
        print(f'{id}: Не является числом')
        return
    field = input('Введите поле которое хотите изменить: ')
    value = input('Введите новое значение: ')
    try:
        task_manager.change_data(id, field, value)
    except IdNotFoundException:
        print('Задача не найдена.')
        return
    except KeyError:
        print('Поле не найдено.')
        return
    print('Данные изменены')


def show_tasks(task_manager: TaskManager):
    """Показывает данные всех задач."""
    print('Список задач:')
    result = task_manager.show_tasks()
    for id, task in result:
        print(
            f"id: {id} Название: {task['name']} Описание: {task['description']} Категория: {task['category']} Дата выполнения: {task['deadline']} Приоритет: {task['priority']} Статус: {task['status']}")


def show_tasks_by_category(task_manager: TaskManager):
    """Показывает задачи по категории."""
    category = input('Введите категорию: ')
    try:
        result = task_manager.show_tasks_by_category(category)
    except KeyError:
        print(f'{category}: Такая категория не найдена.')
        return
    for id, task in result:
        print(
            f"id: {id} Название: {task['name']} Описание: {task['description']} Категория: {task['category']} Дата выполнения: {task['deadline']} Приоритет: {task['priority']} Статус: {task['status']}")


action_dispatcher = {
    'create': add_task,
    'delete': delete_task,
    'search': search_task,
    'change_status': change_task_status,
    'change_field': change_task_field,
    'show': show_tasks,
    'show_category': show_tasks_by_category
}
