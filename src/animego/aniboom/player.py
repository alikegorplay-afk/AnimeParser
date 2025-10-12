from typing import Dict
from urllib.parse import urljoin

import httpx

from ..core.abstract import BasePlayer


class Player(BasePlayer):
    """
    Клиент для работы с видео-плеерами AnimeBoom.
    
    Предоставляет методы для получения информации о доступных
    видео-плеерах, озвучках и ссылках на видео-контент.
    
    Inherits:
        BasePlayer: Базовый интерфейс клиента плееров
        
    Example:
        >>> player = Player()
        >>> player_info = player.get_info(123)
        >>> for player_part in player_info.players:
        ...     print(f"{player_part.title}: {player_part.dubbing_name}")
    """
    
    def __init__(self, domen: str = "https://animego.me", engine: str = "html.parser"):
        """
        Инициализирует клиент плееров.
        
        Args:
            domen (str): Базовый URL сайта
            engine (str): Движок для парсинга HTML
        """
        super().__init__(domen, engine)

    def get_info(self, id: str | int):
        """
        Получает информацию о видео-плеерах для указанного ID аниме.
        
        Args:
            id (str | int): ID аниме
            
        Returns:
            Player: Объект с информацией о плеерах и озвучках
            
        Raises:
            httpx.HTTPError: При ошибках HTTP-запроса
            StatusError: При неуспешном статусе ответа
            NotFindError: При отсутствии контента в ответе
        """
        data: Dict[str, str] = self.fetch(
            urljoin(self.domen, f"anime/{id}/player"), "get", headers=self.base_headers
        )
        return self.parse_data(data)

    def fetch(self, url: str, method: str = "GET", *args, **kwargs) -> Dict[str, str]:
        """
        Выполняет HTTP-запрос к API плееров.
        
        Args:
            url (str): URL для запроса
            method (str): HTTP-метод (GET, POST, etc.)
            
        Returns:
            Dict[str, str]: JSON-ответ от API
            
        Raises:
            httpx.HTTPError: При ошибках HTTP-запроса
        """
        response = httpx.request(method, url, *args, **kwargs)
        response.raise_for_status()

        return response.json()