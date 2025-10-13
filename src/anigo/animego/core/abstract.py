from abc import ABC, abstractmethod
from typing import Dict, Union
from urllib.parse import urljoin

import httpx

from bs4 import Tag

from ..parser.player_parser import PlayerParser, PlayerPart
from ..parser.mpd_parser import MpdParser

from ..models import CvhData, CvhItems

from ...exceptions import StatusError, NotFindError, DataIncorrectError


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
        
        
class BaseMpd(ABC):
    """Базовый класс для получения MPD данных"""
    
    def __init__(self, engine: str = 'html.parser', domain: str = 'https://animego.me'):
        self.engine = engine
        self.domain = domain
        self._headers = {
            'Referer': domain,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self._parser = MpdParser(self.engine)
    
    @staticmethod
    def _normalize_url(url: Union[str, PlayerPart]) -> str:
        """Нормализует URL, добавляя схему https://"""
        if isinstance(url, str):
            url_str = url
        elif isinstance(url, PlayerPart):
            url_str = url.url
        else:
            raise TypeError(f"Неподдерживаемый тип: {type(url).__name__}")
        
        return urljoin('https:', url_str)
    
    @abstractmethod
    def get_mpd(self, url: Union[str, PlayerPart]) -> str:
        """Получить MPD"""
        pass
    
    def _fetch(self, url: str, method: str = "GET", **kwargs) -> str:
        """Выполнить HTTP запрос"""
        headers = {**self._headers, **kwargs.pop('headers', {})}
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()
                return response.text
        except httpx.HTTPStatusError as e:
            raise DataIncorrectError(f"HTTP error {e.response.status_code} for {url}") from e
        except httpx.RequestError as e:
            raise DataIncorrectError(f"Request failed for {url}: {str(e)}") from e
        

class BaseCVH:
    """
    Класс для работы с видео-контентом через CDN Videohub API.
    
    Attributes:
        URL_PLAYLIST (str): URL endpoint для получения плейлиста
        engine (str): Парсер для BeautifulSoup (по умолчанию 'html.parser')
        domain (str): Домен сайта (по умолчанию 'https://animego.me')
        _mpd (MpdController): Контроллер для работы с MPD-потоками
    """
    
    URL_PLAYLIST = 'https://plapi.cdnvideohub.com/api/v1/player/sv/playlist'
    URL_VIDEO = 'https://plapi.cdnvideohub.com/api/v1/player/sv/video/'
    
    def __init__(self, engine: str = "html.parser", domain: str = "https://animego.me"):
        """
        Инициализация CVH-парсера.
        
        Args:
            engine: Парсер для BeautifulSoup (по умолчанию 'html.parser')
            domain: Базовый домен сайта (по умолчанию 'https://animego.me')
        """
        self.engine = engine
        self.domain = domain
    
    def _build_playlist_params(self, player: Tag) -> dict:
        return {
            'pub': player['data-publisher-id'],
            'aggr': player['data-aggregator'], 
            'id': player['data-title-id'],
        }
    
    def _data_correct(self, data: dict) -> CvhData:
        return CvhData(
            title=data['titleName'],
            is_serial=data['isSerial'],
            items=[
                CvhItems(
                    cvh_id=item['cvhId'],
                    name=item['name'],
                    vk_id = item['vkId'],
                    voice_studio = item['voiceStudio'],
                    voice_type = item['voiceType'],
                    season = item['season'],
                    episode = item['episode']
                    ) for item in data['items']
            ]
        )