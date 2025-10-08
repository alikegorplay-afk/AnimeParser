class NotFindError(Exception):
    """Указывет на отсутиствие необходимых данных"""


class StatusError(Exception):
    """Указывет на неверный статус ответа"""


from .utils import not_find
