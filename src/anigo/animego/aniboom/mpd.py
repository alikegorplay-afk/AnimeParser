import json


from ..models import PlayerPart, EmbedData
from ..core.abstract import BaseMpd
from ...exceptions import DataIncorrectError


class MpdController(BaseMpd):
    """Контроллер для получения видео данных"""
    
    def get_mpd(self, url: str | PlayerPart) -> str:
        """Получить MPD"""
        return self._fetch(
            self.get_mpd_url(url)
        )
    
    def get_m3u8_url(self, url: str | PlayerPart) -> str:
        """Получить M3U8 URL"""
        return self.get_full_data(url).m3u8_url
    
    def get_mpd_url(self, url: str | PlayerPart) -> str:
        """Получить MPD URL"""
        return self.get_full_data(url).mpd_url
    
    def get_full_data(self, url: str | PlayerPart) -> EmbedData:
        """Получить все данные видео"""
        embed_data = self._fetch_embed_data(url)
        print(embed_data)
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
    
    def _fetch_embed_data(self, url: str) -> dict:
        """Получить данные embed из HTML"""
        normalized_url = self._normalize_url(url)
        html_content = self._fetch(normalized_url)
        return self._parser.parse_aniboom_html(html_content)
    