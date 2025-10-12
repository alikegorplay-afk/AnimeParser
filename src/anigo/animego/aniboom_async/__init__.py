from urllib.parse import quote, urljoin
from contextlib import asynccontextmanager 

import httpx
import aiofiles

from core.parsers import BasicAnimeApi

from ..parser.anime_parser import AnimeBoomParser
from ..models import PlayerPart
from .pagination import AsyncAniBoomPagination
from .player import AsyncPlayer
from .mpd import AsyncMpdController

class AsyncAniBoom(BasicAnimeApi):
    """
    Асинхронный клиент для работы с AnimeBoom API.
    
    Предоставляет высокопроизводительный интерфейс для работы с сайтом AnimeBoom
    с использованием асинхронных запросов. Идеально подходит для веб-приложений
    и скриптов, требующих параллельной обработки множества запросов.
    
    Attributes:
        session (httpx.AsyncClient): Асинхронный HTTP-клиент
        _aniboom (AnimeBoomParser): Парсер детальной информации об аниме
        _player (AsyncPlayer): Асинхронный клиент для работы с видео-плеерами
        
    Inherits:
        BasicAnimeApi: Базовый интерфейс API-клиента
        
    Example:
        >>> import asyncio
        >>> async def main():
        ...     async with httpx.AsyncClient() as session:
        ...         client = AsyncAniBoom(session)
        ...         # Параллельный поиск
        ...         anime_task = client.get_info("https://animeboom.ru/anime/123")
        ...         player_task = client.get_player_info(123)
        ...         anime, players = await asyncio.gather(anime_task, player_task)
        ...         print(anime.title, players.title)
    """
    
    def __init__(
        self,
        session: httpx.AsyncClient,
        engine: str = "html.parser",
        domen: str = "https://animego.me",
    ):
        """
        Инициализирует асинхронный клиент AnimeBoom.
        
        Args:
            session (httpx.AsyncClient): Готовый асинхронный HTTP-клиент
            engine (str): Движок для парсинга HTML
            domen (str): Базовый URL сайта AnimeBoom
        """
        super().__init__(domen, engine)
        self._aniboom = AnimeBoomParser(engine)
        self._player = AsyncPlayer(session, domen, engine)
        self._mpd = AsyncMpdController(session, engine, domen)
        self.session = session

    async def get_info(self, url: str):
        """
        Асинхронно получает детальную информацию об аниме по URL.
        
        Args:
            url (str): Полный URL страницы аниме
            
        Returns:
            AniBoomAnime: Объект с полной информацией об аниме
            
        Raises:
            httpx.HTTPError: При ошибках HTTP-запроса
            NotFound: При отсутствии обязательных элементов на странице
            
        Example:
            >>> async with httpx.AsyncClient() as session:
            ...     client = AsyncAniBoom(session)
            ...     anime = await client.get_info("https://animeboom.ru/anime/123")
            ...     print(anime.title)
        """
        response = await self.session.get(url, follow_redirects=True)
        response.raise_for_status()

        return self._aniboom.parse_anime(response.text)

    async def find_anime(self, query: str):
        """
        Асинхронно ищет аниме по запросу с поддержкой пагинации.
        
        Args:
            query (str): Поисковый запрос (название аниме)
            
        Returns:
            AsyncAniBoomPagination: Асинхронный объект пагинации
            
        Example:
            >>> async with httpx.AsyncClient() as session:
            ...     client = AsyncAniBoom(session)
            ...     pagination = await client.find_anime("атака титанов")
            ...     async for page in pagination:
            ...         for anime in page:
            ...             print(anime.title)
        """
        return await AsyncAniBoomPagination._find(
            urljoin(self.domen, f"search/anime?q={quote(query)}&type=list&page={'{}'}"),
            self.session,
            self.engine,
        )

    async def find_manga(self, query: str):
        """
        Асинхронно ищет мангу по запросу с поддержкой пагинации.
        
        Args:
            query (str): Поисковый запрос (название манги)
            
        Returns:
            AsyncAniBoomPagination: Асинхронный объект пагинации
        """
        return await AsyncAniBoomPagination._find(
            urljoin(self.domen, f"search/manga?q={quote(query)}&type=list&page={'{}'}"),
            self.session,
            self.engine,
        )

    async def find_people(self, query: str):
        """
        Асинхронно ищет людей (авторов, актеров) по запросу.
        
        Args:
            query (str): Поисковый запрос (имя человека)
            
        Returns:
            AsyncAniBoomPagination: Асинхронный объект пагинации
        """
        return await AsyncAniBoomPagination._find(
            urljoin(
                self.domen, f"search/people?q={quote(query)}&type=list&page={'{}'}"
            ),
            self.session,
            self.engine,
        )

    async def get_player_info(self, id: str | int):
        """
        Асинхронно получает информацию о видео-плеерах для аниме.
        
        Args:
            id (str | int): ID аниме
            
        Returns:
            Player: Объект с информацией о доступных плеерах и озвучках
            
        Example:
            >>> async with httpx.AsyncClient() as session:
            ...     client = AsyncAniBoom(session)
            ...     player_info = await client.get_player_info(123)
            ...     for player in player_info.players:
            ...         print(f"{player.title}: {player.dubbing_name}")
        """
        return await self._player.get_info(id)
    
    def get_aniboom_data(self, url: str | PlayerPart):
        return self._mpd.get_full_data(url)
    
    async def get_mpd_content(self, url: str | PlayerPart) -> str:
        """Получить содержимое MPD файла"""
        return await self._mpd.get_mpd(url)
         
    async def save_mpd_to_file(self, url: str | PlayerPart, filename: str):
        """Сохранить MPD в файл"""
        async with aiofiles.open(filename, 'w') as f:
            await f.write(
                await self.get_mpd_content(url)
            )
    
    @classmethod
    @asynccontextmanager 
    async def create_session(cls, engine: str = "html.parser", domen: str = "https://animego.me"):
        session = None
        try:
            async with httpx.AsyncClient() as session:
                yield cls(session, engine, domen)
        finally:
            if session is None:
                return
            elif not session.is_closed:
                session.aclose()
            else:
                return