"""
AnimeBoom Parser Package

Пакет для парсинга аниме с сайта AnimeBoom.ru
Предоставляет синхронные и асинхронные клиенты, парсеры страниц и плееров.

Основные компоненты:
- AniBoom: Синхронный клиент для работы с API
- AsyncAniBoom: Асинхронный клиент для высокопроизводительных задач
- PlayerParser: Парсер видео-плееров и озвучек
- AnimeBoomParser: Парсер страниц аниме
- AnimeBoomPageParser: Парсер списков аниме

Пример использования:
    >>> from aniboom_parser import AniBoom, PlayerParser
    >>> client = AniBoom()
    >>> anime = client.get_anime("shingeki-no-kyojin")
    >>> players = PlayerParser().parse_player(html_code)
"""

__all__ = [
    "AniBoom",
    "AsyncAniBoom",
    "PlayerParser",
    "AnimeBoomPageParser",
    "AnimeBoomParser",
]

from .aniboom import AniBoom
from .aniboom_async import AsyncAniBoom

from .parser import PlayerParser, AnimeBoomParser, AnimeBoomPageParser
