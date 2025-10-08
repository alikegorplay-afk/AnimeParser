from abc import ABC, abstractmethod
from typing import List

from bs4 import BeautifulSoup, Tag, _IncomingMarkup

from .models import BaseAnimeInfo, AnimeRow, BaseMiniAnimeInfo
from .pagination import BasePagination


class BasicAnimeApi(ABC):
    """
    Абстрактный базовый класс для API-клиентов аниме-сайтов.
    
    Определяет общий интерфейс для работы с различными аниме-платформами.
    Реализации должны предоставлять специфичные для каждого сайта методы
    получения данных.
    
    Attributes:
        domen (str): Базовый URL целевого сайта
        engine (str): Движок для парсинга HTML (по умолчанию 'html.parser')
        
    Methods:
        get_info: Получение детальной информации об аниме
        find_anime: Поиск аниме с пагинацией
    """
    
    def __init__(self, domen: str = "https://animego.me", engine: str = "html.parser"):
        """
        Инициализирует базовый API-клиент.
        
        Args:
            domen (str): Базовый URL сайта для парсинга
            engine (str): Движок для BeautifulSoup
        """
        self.domen = domen
        self.engine = engine

    @abstractmethod
    def get_info(self, url: str) -> BaseAnimeInfo:
        """
        Абстрактный метод получения детальной информации об аниме.
        
        Args:
            url (str): URL страницы аниме
            
        Returns:
            BaseAnimeInfo: Объект с полной информацией об аниме
            
        Raises:
            Зависит от реализации (HTTP ошибки, парсинг ошибки и т.д.)
        """
        pass

    @abstractmethod
    def find_anime(self, url: str) -> BasePagination:
        """
        Абстрактный метод поиска аниме с поддержкой пагинации.
        
        Args:
            url (str): URL страницы поиска или категории
            
        Returns:
            BasePagination: Объект пагинации с результатами поиска
        """
        pass


class BasicAnimeParserMini(ABC):
    """
    Абстрактный парсер для извлечения базовой информации из карточек аниме.
    
    Используется для парсинга элементов в списках, поисковых результатах,
    категориях и других местах, где представлена краткая информация.
    
    Attributes:
        engine (str): Движок для парсинга HTML
        
    Methods:
        parse_anime: Основной метод парсинга карточки аниме
        _find_title: Извлечение названия (абстрактный)
        _find_poster: Извлечение URL постера (абстрактный) 
        _find_url: Извлечение ссылки на страницу (абстрактный)
    """
    
    def __init__(self, engine: str = "html.parser"):
        """
        Инициализирует базовый парсер.
        
        Args:
            engine (str): Движок для BeautifulSoup
        """
        self.engine: str = engine

    def parse_anime(
        self, html_code: _IncomingMarkup | BeautifulSoup
    ) -> BaseMiniAnimeInfo:
        """
        Парсит HTML-код и возвращает базовую информацию об аниме.
        
        Args:
            html_code: HTML-код или готовый BeautifulSoup объект
            
        Returns:
            BaseMiniAnimeInfo: Объект с базовой информацией (название, постер, URL)
            
        Example:
            >>> parser = ConcreteParser()
            >>> anime_card = parser.parse_anime(html_code)
            >>> print(f"{anime_card.title} - {anime_card.url}")
        """
        if not isinstance(html_code, (BeautifulSoup, Tag)):
            soup = BeautifulSoup(html_code, self.engine)
        else:
            soup = html_code

        return BaseMiniAnimeInfo(
            self._find_title(soup), 
            self._find_poster(soup), 
            self._find_url(soup)
        )

    @abstractmethod
    def _find_title(self, soup: BeautifulSoup) -> str:
        """
        Абстрактный метод извлечения названия аниме.
        
        Args:
            soup (BeautifulSoup): Объект для парсинга HTML
            
        Returns:
            str: Название аниме
        """
        ...

    @abstractmethod
    def _find_poster(self, soup: BeautifulSoup) -> str:
        """
        Абстрактный метод извлечения URL постера аниме.
        
        Args:
            soup (BeautifulSoup): Объект для парсинга HTML
            
        Returns:
            str: URL изображения постера
        """
        ...

    @abstractmethod
    def _find_url(self, soup: BeautifulSoup) -> str:
        """
        Абстрактный метод извлечения ссылки на страницу аниме.
        
        Args:
            soup (BeautifulSoup): Объект для парсинга HTML
            
        Returns:
            str: URL страницы аниме
        """
        ...


class BasicAnimeParser(BasicAnimeParserMini):
    """
    Абстрактный парсер для извлечения полной информации об аниме.
    
    Расширяет BasicAnimeParserMini, добавляя методы для получения
    детальной информации: описания, характеристик и дополнительных данных.
    
    Inherits:
        BasicAnimeParserMini: Все методы и атрибуты родительского класса
        
    Methods:
        parse_anime: Переопределен для возврата полной информации
        _find_info: Извлечение дополнительной информации (абстрактный)
        _find_description: Извлечение описания (абстрактный)
    """
    
    def __init__(self, engine: str = "html.parser"):
        """
        Инициализирует расширенный парсер.
        
        Args:
            engine (str): Движок для BeautifulSoup
        """
        self.engine: str = engine

    def parse_anime(self, html_code: _IncomingMarkup) -> BaseAnimeInfo:
        """
        Парсит HTML-код и возвращает полную информацию об аниме.
        
        Args:
            html_code: HTML-код страницы аниме
            
        Returns:
            BaseAnimeInfo: Объект с полной информацией об аниме
            
        Example:
            >>> parser = ConcreteDetailParser()
            >>> anime = parser.parse_anime(html_code)
            >>> print(f"{anime.title}\n{anime.description}")
        """
        soup = BeautifulSoup(html_code, self.engine)

        return BaseAnimeInfo(
            self._find_title(soup),
            self._find_url(soup),
            self._find_poster(soup),
            self._find_description(soup),
            self._find_info(soup),
        )

    @abstractmethod
    def _find_info(self, soup: BeautifulSoup) -> List[AnimeRow]:
        """
        Абстрактный метод извлечения дополнительной информации об аниме.
        
        Args:
            soup (BeautifulSoup): Объект для парсинга HTML
            
        Returns:
            List[AnimeRow]: Список характеристик аниме (тип, жанр, год и т.д.)
        """
        ...

    @abstractmethod
    def _find_description(self, soup: BeautifulSoup) -> str:
        """
        Абстрактный метод извлечения описания аниме.
        
        Args:
            soup (BeautifulSoup): Объект для парсинга HTML
            
        Returns:
            str: Текст описания аниме
        """
        ...