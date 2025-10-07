from abc import ABC, abstractmethod
from typing import Dict, List

from bs4 import _IncomingMarkup
from .models import BaseMiniAnimeInfo

class BasePagination(ABC):
    """Абстрактный класс для постраничной навигации и парсинга списка аниме.
    
    Этот класс предоставляет базовую функциональность для работы с пагинацией:
    навигацию по страницам, кэширование результатов и абстрактные методы для 
    реализации конкретной логики парсинга.
    
    Attributes:
        url (str): Базовый URL для пагинации
        engine (str): Движок для парсинга HTML (по умолчанию 'html.parser')
        current_page (int): Текущая страница (начинается с 1)
        max_page (int): Максимальное количество страниц (0 означает неизвестно)
        cache (Dict[int, List[BaseMiniAnimeInfo]]): Кэш распарсенных результатов по страницам
        args: Дополнительные позиционные аргументы
        kwargs: Дополнительные именованные аргументы
    
    Examples:
        >>> class MyAnimePagination(Pagination):
        ...     def fetch(self, url, *args, **kwargs):
        ...         # реализация загрузки HTML
        ...         pass
        ...     def parse_anime(self, html_code):
        ...         # реализация парсинга аниме
        ...         pass
        ...
        >>> paginator = MyAnimePagination("https://example.com/anime/list")
        >>> first_page = paginator.select_page(1)
        >>> next_page = paginator.next_page()
    """
    
    def __init__(self, url: str, engine: str = 'html.parser', *args, **kwargs):
        """Инициализирует пагинатор.
        
        Args:
            url (str): Базовый URL для пагинации
            engine (str, optional): Движок для BeautifulSoup. По умолчанию 'html.parser'
            *args: Дополнительные позиционные аргументы для fetch метода
            **kwargs: Дополнительные именованные аргументы для fetch метода
        """
        self.url: str = url
        self.engine: str = engine
        
        self.current_page = 1
        self.max_page = 0
        
        self.cache: Dict[int, List[BaseMiniAnimeInfo]] = {}
        
        self.args = args
        self.kwargs = kwargs
        
    def next_page(self) -> List[BaseMiniAnimeInfo] | None:
        """Переходит на следующую страницу.
        
        Returns:
            List[BaseMiniAnimeInfo] | None: Список аниме со следующей страницы или None, 
            если следующей страницы не существует
        
        Examples:
            >>> next_anime = paginator.next_page()
            >>> if next_anime:
            ...     for anime in next_anime:
            ...         print(anime.title)
        """
        return self.select_page(self.current_page + 1)
    
    def back_page(self) -> List[BaseMiniAnimeInfo] | None:
        """Переходит на предыдущую страницу.
        
        Returns:
            List[BaseMiniAnimeInfo] | None: Список аниме с предыдущей страницы или None, 
            если предыдущей страницы не существует
        
        Examples:
            >>> prev_anime = paginator.back_page()
            >>> if prev_anime:
            ...     print(f"Вернулись на страницу {paginator.current_page}")
        """
        return self.select_page(self.current_page - 1)
    
    def select_page(self, page: int) -> List[BaseMiniAnimeInfo] | None:
        """Выбирает конкретную страницу для парсинга.
        
        Args:
            page (int): Номер страницы для загрузки (начинается с 1)
            
        Returns:
            List[BaseMiniAnimeInfo] | None: Список аниме с указанной страницы или None, 
            если страница не существует
            
        Notes:
            - Использует кэширование: если страница уже была загружена, возвращает данные из кэша
            - Проверяет валидность номера страницы (должна быть в диапазоне 1..max_page)
            - Если max_page = 0, проверка верхней границы не выполняется
            
        Examples:
            >>> page_5 = paginator.select_page(5)
            >>> if page_5:
            ...     print(f"Найдено {len(page_5)} аниме на странице 5")
        """
        if not (0 < page <= self.max_page) and self.max_page != 0:
            return None
            
        # Проверяем кэш перед загрузкой
        if page in self.cache:
            self.current_page = page
            return self.cache[page]
        
        self.current_page = page
        result = self.parse_anime(
            self.fetch(
                self.url, *self.args, **self.kwargs
            )
        )
        
        # Сохраняем в кэш
        self.cache[page] = result
        return result
    
    @abstractmethod
    def fetch(self, url: str, *args, **kwargs) -> str:
        """Абстрактный метод для загрузки HTML-кода страницы.
        
        Args:
            url (str): URL для загрузки
            *args: Дополнительные позиционные аргументы
            **kwargs: Дополнительные именованные аргументы
            
        Returns:
            str: HTML-код загруженной страницы
            
        Raises:
            NotImplementedError: Должен быть реализован в дочернем классе
            
        Notes:
            Реализация этого метода должна включать логику HTTP-запросов,
            обработку ошибок и возврат HTML в виде строки.
        """
        pass
    
    @abstractmethod
    def parse_anime(self, html_code: _IncomingMarkup) -> List[BaseMiniAnimeInfo]:
        """Абстрактный метод для парсинга HTML и извлечения списка аниме.
        
        Args:
            html_code (_IncomingMarkup): HTML-код страницы для парсинга
            
        Returns:
            List[BaseMiniAnimeInfo]: Список объектов с информацией об аниме
            
        Raises:
            NotImplementedError: Должен быть реализован в дочернем классе
            
        Notes:
            Реализация этого метода должна использовать BeautifulSoup или другую
            библиотеку для парсинга HTML и преобразования данных в объекты BaseMiniAnimeInfo.
        """
        pass
    
    def __str__(self):
        return (
            "Номер страницы: {} из {} загружены страницы, {}".format(
                self.current_page,
                self.max_page,
                ', '.join(
                    [str(num) for num in self.cache.keys()]
                )
            )
        )
        
    def get_current_page(self):
        if self.current_page in self.cache:
            return self.cache[self.current_page]
        return self.select_page(self.current_page)
    
class AsyncBasePagination(BasePagination):
    async def next_page(self) -> List[BaseMiniAnimeInfo] | None:
        """Переходит на следующую страницу.
        
        Returns:
            List[BaseMiniAnimeInfo] | None: Список аниме со следующей страницы или None, 
            если следующей страницы не существует
        
        Examples:
            >>> next_anime = paginator.next_page()
            >>> if next_anime:
            ...     for anime in next_anime:
            ...         print(anime.title)
        """
        return await self.select_page(self.current_page + 1)
    
    async def back_page(self) -> List[BaseMiniAnimeInfo] | None:
        """Переходит на предыдущую страницу.
        
        Returns:
            List[BaseMiniAnimeInfo] | None: Список аниме с предыдущей страницы или None, 
            если предыдущей страницы не существует
        
        Examples:
            >>> prev_anime = paginator.back_page()
            >>> if prev_anime:
            ...     print(f"Вернулись на страницу {paginator.current_page}")
        """
        return await self.select_page(self.current_page - 1)
    
    async def select_page(self, page: int) -> List[BaseMiniAnimeInfo] | None:
        """Выбирает конкретную страницу для парсинга.
        
        Args:
            page (int): Номер страницы для загрузки (начинается с 1)
            
        Returns:
            List[BaseMiniAnimeInfo] | None: Список аниме с указанной страницы или None, 
            если страница не существует
            
        Notes:
            - Использует кэширование: если страница уже была загружена, возвращает данные из кэша
            - Проверяет валидность номера страницы (должна быть в диапазоне 1..max_page)
            - Если max_page = 0, проверка верхней границы не выполняется
            
        Examples:
            >>> page_5 = paginator.select_page(5)
            >>> if page_5:
            ...     print(f"Найдено {len(page_5)} аниме на странице 5")
        """
        if not (0 < page <= self.max_page) and self.max_page != 0:
            return None
            
        # Проверяем кэш перед загрузкой
        if page in self.cache:
            self.current_page = page
            return self.cache[page]
        
        self.current_page = page
        result = self.parse_anime(
            await self.fetch(
                self.url, *self.args, **self.kwargs
            )
        )
        
        # Сохраняем в кэш
        self.cache[page] = result
        return result
    
    @abstractmethod
    async def fetch(self, url: str, *args, **kwargs) -> str:
        """Абстрактный метод для загрузки HTML-кода страницы.
        
        Args:
            url (str): URL для загрузки
            *args: Дополнительные позиционные аргументы
            **kwargs: Дополнительные именованные аргументы
            
        Returns:
            str: HTML-код загруженной страницы
            
        Raises:
            NotImplementedError: Должен быть реализован в дочернем классе
            
        Notes:
            Реализация этого метода должна включать логику HTTP-запросов,
            обработку ошибок и возврат HTML в виде строки.
        """
        pass
    