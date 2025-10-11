from dataclasses import dataclass
from abc import ABC
from typing import List, Any


@dataclass
class AnimeRow:
    """Хранит отдельную характеристику аниме в формате ключ-значение.

    Attributes:
        name (str): Название характеристики (например, "Жанр", "Год выпуска")
        value (str | List[str]): Значение характеристики. Может быть строкой или списком строк
        original (Any): Исходные raw-данные, из которых была получена информация

    Examples:
        >>> row = AnimeRow(
        ...     name="Жанры",
        ...     value=["Фэнтези", "Приключения"],
        ...     original=["Fantasy", "Adventure"]
        ... )
    """

    name: str
    value: str | List[str]
    original: Any


@dataclass
class BaseMiniAnimeInfo(ABC):
    """Абстрактный базовый класс для краткой информации об аниме.

    Attributes:
        title (str): Название аниме
        url (str): URL-адрес страницы с аниме
        poster_url (str): URL-адрес постера/обложки

    Notes:
        Этот класс является абстрактным и не может быть инстанциирован напрямую.
        Требует реализации свойства ID в дочерних классах.
    """

    title: str
    url: str
    poster_url: str

    @property
    def ID(self) -> str:
        """Уникальный идентификатор аниме.

        Returns:
            str: Уникальный идентификатор (обычно извлекается из URL или внешней системы)

        Examples:
            >>> class ShikimoriAnimeInfo(BaseMiniAnimeInfo):
            ...     @property
            ...     def ID(self):
            ...         return self.url.split("/")[-1]
        """
        return self.url.split("-")[-1]


@dataclass
class BaseAnimeInfo(BaseMiniAnimeInfo):
    """Класс для полной информации об аниме с расширенными данными.

    Attributes:
        description (str): Подробное описание/сюжет аниме
        anime_info (List[AnimeRow]): Список характеристик аниме в формате ключ-значение

    Inherits:
        BaseMiniAnimeInfo: Все атрибуты родительского класса

    Notes:
        Требует реализации свойства ID в дочерних классах.
        Все характеристики организованы в виде списка AnimeRow для единообразия.

    Examples:
        >>> anime = BaseAnimeInfo(
        ...     title="Attack on Titan",
        ...     url="https://example.com/aot",
        ...     poster_url="https://example.com/poster.jpg",
        ...     description="История о борьбе человечества с титанами...",
        ...     anime_info=[
        ...         AnimeRow("Год выпуска", "2013", original="2013"),
        ...         AnimeRow("Жанры", ["Экшен", "Драма"], original=["Action", "Drama"])
        ...     ]
        ... )
    """

    description: str
    anime_info: List[AnimeRow]
