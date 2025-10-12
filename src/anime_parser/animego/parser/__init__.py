"""
AnimeBoom Parsers Package

Пакет содержит парсеры для работы с сайтом AnimeBoom.ru.

Доступные классы:
    - AnimeBoomParser: Парсер детальной страницы аниме
    - AnimeBoomPageParser: Парсер карточек аниме в списках
    - PlayerParser: Парсер видео-плееров и озвучек

Пример использования:
    >>> from aniboom_parsers import AnimeBoomParser, PlayerParser
    >>>
    >>> # Парсим страницу аниме
    >>> anime_parser = AnimeBoomParser()
    >>> anime_data = anime_parser.parse_anime(html_code)
    >>>
    >>> # Парсим видео-плееры
    >>> player_parser = PlayerParser()
    >>> player_data = player_parser.parse_player(player_html_code)
"""

__all__ = ["PlayerParser", "AnimeBoomPageParser", "AnimeBoomParser"]

from .anime_parser import AnimeBoomParser
from .page_parser import AnimeBoomPageParser
from .player_parser import PlayerParser
