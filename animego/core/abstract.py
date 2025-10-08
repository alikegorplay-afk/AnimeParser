from abc import ABC, abstractmethod
from typing import Dict

from ..parser.player_parser import PlayerParser

from exceptions import StatusError, NotFindError


class BasePlayer(ABC):
    """
    Абстрактный базовый класс для реализации клиентов видео-плееров.

    Определяет общий интерфейс и базовую функциональность для работы
    с видео-плеерами на различных платформах. Реализует общую логику
    парсинга и валидации данных, оставляя специфичные для платформы
    методы для реализации в дочерних классах.

    Attributes:
        base_headers (Dict[str, str]): Базовые HTTP-заголовки для запросов
        engine (str): Движок для парсинга HTML
        domen (str): Базовый домен целевого сайта

    Methods:
        get_info: Абстрактный метод получения информации о видео
        fetch: Абстрактный метод выполнения HTTP-запросов
        parse_data: Парсит и валидирует данные ответа
        raise_for_data: Валидирует структуру и статус ответа
    """

    def __init__(self, domen: str = "https://animego.me", engine: str = "html.parser"):
        """
        Инициализирует базовый клиент плеера.

        Args:
            domen (str): Базовый URL целевого сайта
            engine (str): Движок для BeautifulSoup парсинга
        """
        self.base_headers: Dict[str, str] = {
            "referer": domen,
            "x-requested-with": "XMLHttpRequest",
        }
        self.engine = engine
        self.domen = domen

    @abstractmethod
    def get_info(self, id: str | int):
        """
        Абстрактный метод для получения информации о видео по ID.

        Должен быть реализован в дочерних классах для конкретной платформы.

        Args:
            id (str | int): Идентификатор видео/эпизода

        Returns:
            Зависит от реализации, обычно объект с информацией о плеерах

        Raises:
            Зависит от реализации, обычно HTTP и парсинг ошибки
        """
        ...

    @abstractmethod
    def fetch(self, url: str, method: str = "GET", *args, **kwargs):
        """
        Абстрактный метод выполнения HTTP-запросов.

        Должен быть реализован в дочерних классах с учетом специфики
        платформы (сессии, куки, аутентификация и т.д.).

        Args:
            url (str): URL для запроса
            method (str): HTTP-метод (GET, POST, etc.)
            *args: Дополнительные позиционные аргументы
            **kwargs: Дополнительные именованные аргументы

        Returns:
            Зависит от реализации, обычно словарь с данными ответа
        """
        ...

    def parse_data(self, data: Dict[str, str]):
        """
        Парсит данные ответа и возвращает структурированную информацию.

        Выполняет валидацию данных и делегирует парсинг контента
        специализированному парсеру PlayerParser.

        Args:
            data (Dict[str, str]): Сырые данные ответа от API

        Returns:
            Player: Объект с информацией о видео-плеерах и озвучках

        Raises:
            TypeError: Если передан неподдерживаемый тип данных
            StatusError: Если статус ответа не 'success'
            NotFindError: Если в ответе отсутствует контент
        """
        self.raise_for_data(data)

        parser = PlayerParser()
        return parser.parse_player(data["content"])

    @staticmethod
    def raise_for_data(data: Dict[str, str]):
        """
        Валидирует структуру и статус данных ответа.

        Проверяет:
        - Тип данных (должен быть dict)
        - Статус ответа (должен быть 'success')
        - Наличие контента для парсинга

        Args:
            data (Dict[str, str]): Данные для валидации

        Raises:
            TypeError: Если данные не являются словарем
            StatusError: Если статус ответа не успешный
            NotFindError: Если отсутствует контент для парсинга
        """
        if not isinstance(data, dict):
            raise TypeError(f"Неподдерживаемый тип: {type(data).__name__}")

        if data.get("status") != "success":
            raise StatusError(f"Неожиданный статус ответа: {data.get('status')}")

        elif not data.get("content"):
            raise NotFindError("Не был обнаружен 'content'")