class TaskManagerException(BaseException):
    pass

class WrongDeadlineException(BaseException):
    pass

class NullValueException(BaseException):
    def __init__(self):
        super().__init__(f'Поле обязательно для заполнения.')

class NotValidPriorityException(BaseException):
    def __init__(self, values):
        super().__init__(f'{value}: Значение не является приоритетом')


class IdNotFoundException(BaseException):
    def __init__(self):
        super().__init__()