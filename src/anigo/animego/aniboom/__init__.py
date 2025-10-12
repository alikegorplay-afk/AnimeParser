from urllib.parse import quote, urljoin

import httpx

from ...core.parsers import BasicAnimeApi

from ..models import PlayerPart
from ..parser import AnimeBoomParser
from .pagination import AniBoomPagination
from .player import Player
from .mpd import MpdController


class AniBoom(BasicAnimeApi):
    """
    Основной синхронный клиент для работы с AnimeBoom API.
    
    Предоставляет удобный интерфейс для поиска и получения информации
    об аниме, манге, персонах и видео-плеерах с сайта AnimeBoom.
    
    Attributes:
        _aniboom (AnimeBoomParser): Парсер детальной информации об аниме
        _player (Player): Клиент для работы с видео-плеерами
        
    Inherits:
        BasicAnimeApi: Базовый интерфейс API-клиента
        
    Example:
        >>> client = AniBoom()
        >>> # Поиск аниме
        >>> results = client.find_anime("атака титанов")
        >>> # Детальная информация
        >>> anime = client.get_info("https://animeboom.ru/anime/123")
        >>> # Информация о плеерах
        >>> players = client.get_player_info(123)
    """
    
    def __init__(self, engine: str = "html.parser", domain: str = "https://animego.me"):
        """
        Инициализирует клиент AnimeBoom.
        
        Args:
            engine (str): Движок для парсинга HTML
            domain (str): Базовый URL сайта AnimeBoom
        """
        super().__init__(domain, engine)
        self._aniboom = AnimeBoomParser(engine)
        self._player = Player(domain, engine)
        self._mpd = MpdController(engine, domain)

    def get_info(self, url: str):
        """
        Получает детальную информацию об аниме по URL.
        
        Args:
            url (str): Полный URL страницы аниме
            
        Returns:
            AniBoomAnime: Объект с полной информацией об аниме
            
        Raises:
            httpx.HTTPError: При ошибках HTTP-запроса
            NotFound: При отсутствии обязательных элементов на странице
            
        Example:
            >>> anime = client.get_info("https://animeboom.ru/anime/attack-on-titan-123")
            >>> print(anime.title, anime.synonyms)
        """
        response = httpx.get(url, follow_redirects=True)
        response.raise_for_status()

        return self._aniboom.parse_anime(response.text)

    def find_anime(self, query: str):
        """
        Ищет аниме по запросу с поддержкой пагинации.
        
        Args:
            query (str): Поисковый запрос (название аниме)
            
        Returns:
            AniBoomPagination: Объект пагинации с результатами поиска
            
        Example:
            >>> pagination = client.find_anime("наруто")
            >>> for page in pagination:
            ...     for anime in page:
            ...         print(anime.title)
        """
        return AniBoomPagination._find(
            urljoin(self.domen, f"search/anime?q={quote(query)}&type=list&page={'{}'}"),
            self.engine,
        )

    def find_manga(self, query: str):
        """
        Ищет мангу по запросу с поддержкой пагинации.
        
        Args:
            query (str): Поисковый запрос (название манги)
            
        Returns:
            AniBoomPagination: Объект пагинации с результатами поиска
        """
        return AniBoomPagination._find(
            urljoin(self.domen, f"search/manga?q={quote(query)}&type=list&page={'{}'}"),
            self.engine,
        )

    def find_people(self, query: str):
        """
        Ищет людей (авторов, актеров) по запросу с поддержкой пагинации.
        
        Args:
            query (str): Поисковый запрос (имя человека)
            
        Returns:
            AniBoomPagination: Объект пагинации с результатами поиска
        """
        return AniBoomPagination._find(
            urljoin(
                self.domen, f"search/people?q={quote(query)}&type=list&page={'{}'}"
            ),
            self.engine,
        )

    def get_player_info(self, id: str | int):
        """
        Получает информацию о видео-плеерах для конкретного аниме.
        
        Args:
            id (str | int): ID аниме
            
        Returns:
            Player: Объект с информацией о доступных плеерах и озвучках
            
        Example:
            >>> player_info = client.get_player_info(123)
            >>> for player in player_info.players:
            ...     print(f"{player.title}: {player.url}")
        """
        if isinstance(id, str) and id.startswith('http'):
            id = id.split("-")[-1]
        return self._player.get_info(id)
    
    def get_aniboom_data(self, url: str | PlayerPart):
        return self._mpd.get_full_data(url)
    
    def get_mpd_content(self, url: str | PlayerPart) -> str:
        """Получить содержимое MPD файла"""
        return self._mpd.get_mpd(url)
        
        
    def save_mpd_to_file(self, url: str | PlayerPart, filename: str):
        """Сохранить MPD в файл"""
        with open(filename, 'w') as f:
            f.write(
                self.get_mpd_content(url)
            )