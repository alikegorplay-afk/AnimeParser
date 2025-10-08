from exceptions import NotFindError


def not_find(query: str) -> NotFindError:
    return NotFindError(f"Не был найден атрибут: '{query}'")
