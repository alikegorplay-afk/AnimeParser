import json

from urllib.parse import urljoin
from bs4 import BeautifulSoup

from ..core.abstract import BaseCVH
from ..models import PlayerPart, CvhData, CvhItems
from ...exceptions import DataIncorrectError, not_find
from ..aniboom.mpd import MpdController

class CVH(BaseCVH):
    """
    Класс для работы с видео-контентом через CDN Videohub API.
    
    Attributes:
        URL_PLAYLIST (str): URL endpoint для получения плейлиста
        engine (str): Парсер для BeautifulSoup (по умолчанию 'html.parser')
        domain (str): Домен сайта (по умолчанию 'https://animego.me')
        _mpd (MpdController): Контроллер для работы с MPD-потоками
    """
    
    def __init__(self, engine = "html.parser", domain = "https://animego.me"):
        super().__init__(engine, domain)
        self._mpd = MpdController(engine, domain)
    
    def _get_video(self, vk_id: str | int) -> dict:
        return json.loads(
            self._mpd._fetch(
            urljoin(
                self.URL_VIDEO, vk_id
            ), "GET")
        )
    
    def get_video_data(self, vk_id: str | int | CvhItems):
        if isinstance(vk_id, (str, int)):
            pass
        elif isinstance(vk_id, CvhItems):
            vk_id = vk_id.vk_id
        else:
            raise TypeError(f"Неподдерживаемый тип: {type(vk_id).__name__}")
        return self._get_video(vk_id)
    
    def get_playlist(self, url: str | PlayerPart) -> CvhData:
        """
        Получает плейлист видео из iframe-контента.
        
        Args:
            url: URL страницы или объект PlayerPart с видео-контентом
            
        Returns:
            dict: JSON-ответ API с данными плейлиста
            
        Raises:
            DataIncorrectError: 
                - Если в данных iframe отсутствуют необходимые атрибуты
                - Если ответ API не является валидным JSON
        """
        soup = BeautifulSoup(self.get_iframe(url), self.engine)
        player = soup.find("video-player")
        if player is None:
            raise not_find("video-player")
        try:
            return self._data_correct(json.loads(
                self._mpd._fetch(
                    self.URL_PLAYLIST,
                    'GET',
                    params = self._build_playlist_params(player)
                )
            ))
        except KeyError as error:
            raise DataIncorrectError(f"Не был найден ключ: [{error.args[-1]}]")
        except json.JSONDecodeError:
            raise DataIncorrectError(f"Ошибка при парсинге 'json'")
    
    def get_iframe(self, url: str | PlayerPart) -> str:
        """
        Получает содержимое iframe по указанному URL.
        
        Args:
            url: URL страницы или объект PlayerPart
            
        Returns:
            str: HTML-содержимое iframe
        """
        return self._mpd._fetch(self._mpd._normalize_url(url))