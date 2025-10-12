import json

import httpx

from ..models import PlayerPart, EmbedData
from ..core.abstract import BaseMpd
from exceptions import DataIncorrectError


class AsyncMpdController(BaseMpd):
    """Контроллер для получения видео данных"""
    def __init__(self, session: httpx.AsyncClient, engine = 'html.parser', domain = 'https://animego.me'):
        super().__init__(engine, domain)
        self._session = session
        
    async def get_mpd(self, url: str | PlayerPart) -> str:
        """Получить MPD"""
        return await self._fetch(
            await self.get_mpd_url(url)
        )
        
    async def get_m3u8_url(self, url: str | PlayerPart) -> str:
        """Получить M3U8 URL"""
        return (await self.get_full_data(url)).m3u8_url
    
    async def get_mpd_url(self, url: str | PlayerPart) -> str:
        """Получить MPD URL"""
        return (await self.get_full_data(url)).mpd_url
    
    async def get_full_data(self, url: str | PlayerPart) -> EmbedData:
        """Получить все данные видео"""
        embed_data = await self._fetch_embed_data(url)
        
        try:
            return EmbedData(
                id=embed_data['id'],
                domain=embed_data['domain'],
                duration=embed_data['duration'],
                poster=embed_data['poster'],
                mpd_url=json.loads(embed_data['dash'])["src"],
                m3u8_url=json.loads(embed_data['hls'])["src"],
                quality=embed_data['quality'],
                quality_video=embed_data['qualityVideo'],
                rating=embed_data['rating']
            )
        except (KeyError, json.JSONDecodeError) as e:
            raise DataIncorrectError(f"Failed to parse embed data: {str(e)}") from e
    
    async def _fetch_embed_data(self, url: str) -> dict:
        """Получить данные embed из HTML"""
        normalized_url = self._normalize_url(url)
        html_content = await self._fetch(normalized_url)
        return self._parser.parse_aniboom_html(html_content)
    
    async def _fetch(self, url, method = "GET", **kwargs):
        headers = {**self._headers, **kwargs.pop('headers', {})}
        
        response = await self._session.request(method, url, **headers)
        response.raise_for_status()
        
        return response.text