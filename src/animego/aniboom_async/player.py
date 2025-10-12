from typing import Dict
from urllib.parse import urljoin

import httpx

from ..core.abstract import BasePlayer


class AsyncPlayer(BasePlayer):
    """
    Асинхронный клиент для работы с видео-плеерами AnimeBoom.
    
    Предоставляет высокопроизводительные методы для получения информации
    о доступных видео-плеерах и озвучках с использованием асинхронных запросов.
    
    Attributes:
        client (httpx.AsyncClient): Асинхронный HTTP-клиент
        
    Inherits:
        BasePlayer: Базовый интерфейс клиента плееров
        
    Example:
        >>> async with httpx.AsyncClient() as session:
        ...     player = AsyncPlayer(session)
        ...     player_info = await player.get_info(123)
        ...     for player_part in player_info.players:
        ...         print(f"{player_part.title}: {player_part.url}")
    """
    
    def __init__(
        self,
        client: httpx.AsyncClient,
        domen: str = "https://animego.me",
        engine: str = "html.parser",
    ):
        """
        Инициализирует асинхронный клиент плееров.
        
        Args:
            client (httpx.AsyncClient): Асинхронный HTTP-клиент
            domen (str): Базовый URL сайта
            engine (str): Движок для парсинга HTML
        """
        super().__init__(domen, engine)
        self.client = client

    async def get_info(self, id: str | int):
        """
        Асинхронно получает информацию о видео-плеерах для аниме.
        
        Args:
            id (str | int): ID аниме
            
        Returns:
            Player: Объект с информацией о плеерах и озвучках
            
        Raises:
            httpx.HTTPError: При ошибках HTTP-запроса
            StatusError: При неуспешном статусе ответа
            NotFindError: При отсутствии контента в ответе
        """
        data: Dict[str, str] = await self.fetch(
            urljoin(self.domen, f"anime/{id}/player"), "get", headers=self.base_headers
        )

        return self.parse_data(data)

    async def fetch(self, url: str, method: str = "GET", *args, **kwargs) -> Dict[str, str]:
        """
        Асинхронно выполняет HTTP-запрос к API плееров.
        
        Args:
            url (str): URL для запроса
            method (str): HTTP-метод (GET, POST, etc.)
            
        Returns:
            Dict[str, str]: JSON-ответ от API
            
        Raises:
            httpx.HTTPError: При ошибках HTTP-запроса
        """
        response = await self.client.request(method, url, *args, **kwargs)
        response.raise_for_status()

        return response.json()