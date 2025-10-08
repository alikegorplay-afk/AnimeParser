from math import ceil

import httpx

from bs4 import BeautifulSoup

from ..parser import AnimeBoomPageParser

from core.pagination import AsyncBasePagination
from exceptions.utils import not_find


class AsyncAniBoomPagination(AsyncBasePagination):
    """
    Асинхронная реализация пагинации для поисковых результатов AnimeBoom.
    
    Обеспечивает асинхронную постраничную навигацию с поддержкой
    конкурентных запросов и эффективным использованием ресурсов.
    
    Attributes:
        MAX_ANIME_IN_PAGE (int): Максимальное количество элементов на странице
        parser (AnimeBoomPageParser): Парсер для обработки карточек аниме
        session (httpx.AsyncClient): Асинхронный HTTP-клиент
        
    Inherits:
        AsyncBasePagination: Базовая асинхронная функциональность пагинации
    """
    
    MAX_ANIME_IN_PAGE = 16

    def __init__(
        self, url: str, session: httpx.AsyncClient, engine: str = "html.parser", *args, **kwargs
    ):
        """
        Инициализирует асинхронный пагинатор.
        
        Args:
            url (str): URL-шаблон с плейсхолдером для номера страницы
            session (httpx.AsyncClient): Асинхронный HTTP-клиент
            engine (str): Движок для парсинга HTML
        """
        super().__init__(url, engine, *args, **kwargs)
        self.parser = AnimeBoomPageParser(self.engine)
        self.session = session

    async def fetch(self, url: str, *args, **kwargs):
        """
        Асинхронно выполняет HTTP-запрос для получения страницы результатов.
        
        Args:
            url (str): URL-шаблон для запроса
            
        Returns:
            str: HTML-код страницы
            
        Raises:
            httpx.HTTPError: При ошибках HTTP-запроса
        """
        response = await self.session.get(
            url.format(self.current_page), *args, **kwargs
        )
        
        response.raise_for_status()
        return response.text

    def parse_anime(self, html_code: str):
        """
        Парсит HTML-код и извлекает список карточек аниме.
        
        Args:
            html_code (str): HTML-код страницы с результатами
            
        Returns:
            list[BaseMiniAnimeInfo]: Список объектов с базовой информацией об аниме
            
        Raises:
            NotFound: Если не удается найти карточки аниме на странице
        """
        soup = BeautifulSoup(html_code, self.engine)
        
        if not (all_anime := soup.find_all("div", class_="animes-grid-item")):
            self.max_page = self.current_page - 1
            self.current_page = self.max_page
            return self.cache[self.current_page]
            
        return [self.parser.parse_anime(anime) for anime in all_anime]

    @classmethod
    async def _find(
        cls, url: str, session: httpx.AsyncClient, engine: str, *args, **kwargs
    ):
        """
        Асинхронный фабричный метод для создания пагинатора.
        
        Args:
            url (str): URL-шаблон для поиска
            session (httpx.AsyncClient): Асинхронный HTTP-клиент
            engine (str): Движок для парсинга HTML
            
        Returns:
            AsyncAniBoomPagination: Настроенный асинхронный объект пагинации
            
        Raises:
            ValueError: Если по запросу не найдено ни одного тайтла
        """
        cls = cls(url, session, engine, *args, **kwargs)
        html = await cls.fetch(url)
        soup = BeautifulSoup(html, engine)
        try:
            cls.max_page = ceil(
                int(soup.find("span", class_="search-county").get_text(strip=True))
                / cls.MAX_ANIME_IN_PAGE
            )
            cls.cache[cls.current_page] = cls.parse_anime(html)
        except AttributeError:
            raise ValueError(f"Не был найден ни один тайтл по URL: {url}")

        return cls

    async def __aiter__(self):
        """
        Асинхронный итератор для постраничного обхода результатов.
        
        Yields:
            list[BaseMiniAnimeInfo]: Результаты для каждой страницы
            
        Example:
            >>> async with httpx.AsyncClient() as session:
            ...     pagination = await AsyncAniBoomPagination._find(url, session, engine)
            ...     async for page_results in pagination:
            ...         for anime in page_results:
            ...             print(anime.title)
        """
        for page in range(1, self.max_page + 1):
            yield await self.select_page(page)