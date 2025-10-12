from math import ceil

import httpx

from bs4 import BeautifulSoup

from ..parser import AnimeBoomPageParser

from core.pagination import BasePagination


class AniBoomPagination(BasePagination):
    """
    Реализация пагинации для поисковых результатов AnimeBoom.
    
    Обеспечивает постраничную навигацию по результатам поиска
    аниме, манги и людей с кэшированием и ленивой загрузкой.
    
    Attributes:
        MAX_ANIME_IN_PAGE (int): Максимальное количество элементов на странице
        parser (AnimeBoomPageParser): Парсер для обработки карточек аниме
        
    Inherits:
        BasePagination: Базовая функциональность пагинации
    """
    
    MAX_ANIME_IN_PAGE = 16

    def __init__(self, url: str, engine: str = "html.parser", *args, **kwargs):
        """
        Инициализирует пагинатор.
        
        Args:
            url (str): URL-шаблон с плейсхолдером для номера страницы
            engine (str): Движок для парсинга HTML
        """
        super().__init__(url, engine, *args, **kwargs)
        self.parser = AnimeBoomPageParser(self.engine)

    def fetch(self, url: str, *args, **kwargs):
        """
        Выполняет HTTP-запрос для получения страницы результатов.
        
        Args:
            url (str): URL-шаблон для запроса
            
        Returns:
            str: HTML-код страницы
            
        Raises:
            httpx.HTTPError: При ошибках HTTP-запроса
        """
        response = httpx.get(url.format(self.current_page), *args, **kwargs)
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
    def _find(cls, url: str, engine: str, *args, **kwargs):
        """
        Фабричный метод для создания пагинатора с предварительной настройкой.
        
        Args:
            url (str): URL-шаблон для поиска
            engine (str): Движок для парсинга HTML
            
        Returns:
            AniBoomPagination: Настроенный объект пагинации
            
        Raises:
            ValueError: Если по запросу не найдено ни одного тайтла
        """
        cls = cls(url, engine, *args, **kwargs)
        html = cls.fetch(url)
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

    def __iter__(self):
        """
        Позволяет итерироваться по всем страницам результатов.
        
        Yields:
            list[BaseMiniAnimeInfo]: Результаты для каждой страницы
            
        Example:
            >>> pagination = AniBoomPagination._find(url, engine)
            >>> for page_results in pagination:
            ...     for anime in page_results:
            ...         print(anime.title)
        """ 
        # FIXME: Короче это костыль из-за либо кривого API то ли моих рук!
        
        last_page = -1
        for page in range(1, self.max_page + 1):
            result = self.select_page(page)
            if last_page == self.current_page:
                break
            
            yield result
            last_page = self.current_page