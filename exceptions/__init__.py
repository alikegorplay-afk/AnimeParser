class NotFindError(Exception):
    """Указывет на отсутиствие необходимых данных"""

class StatusError(Exception):
    """Указывет на неверный статус ответа"""

class DataIncorrectError(Exception):
    """Указывает на то что входные данные инкорректны"""
    
from .utils import not_find as not_find