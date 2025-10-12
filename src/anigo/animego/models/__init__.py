from dataclasses import dataclass
from typing import List

from ...core.models import BaseAnimeInfo


@dataclass
class AniBoomAnime(BaseAnimeInfo):
    """
    Полная информация об аниме с сайта AnimeBoom.

    Расширяет базовую модель аниме дополнительными полями,
    специфичными для AnimeBoom.

    Attributes:
        synonyms: Список альтернативных названий и синонимов аниме

    Inherited Attributes:
        title: Основное название аниме
        url: Ссылка на страницу аниме
        poster_url: URL постера аниме
        description: Описание аниме
        anime_info: Дополнительная информация (жанры, год, статус и т.д.)

    Properties:
        ID: Уникальный идентификатор аниме, извлекаемый из URL

    Example:
        >>> anime = AniBoomAnime(
        ...     title="Атака титанов",
        ...     url="https://animeboom.ru/anime/attack-on-titan-123",
        ...     poster_url="https://example.com/poster.jpg",
        ...     description="Человечество ведет борьбу с титанами...",
        ...     anime_info=[
        ...         AnimeRow("Тип", "ТВ Сериал"),
        ...         AnimeRow("Эпизоды", 75)
        ...     ],
        ...     synonyms=["Shingeki no Kyojin", "Attack on Titan"]
        ... )
        >>> anime.ID
        "123"
    """

    synonyms: List[str]

    @property
    def ID(self) -> str:
        """Извлекает ID аниме из URL."""
        return self.url.split("-")[-1]


@dataclass
class PlayerPart:
    """
    Информация о конкретном видео-плеере для определенной озвучки.

    Представляет связку: плеер + озвучка + ссылка на видео.

    Attributes:
        title: Название видео-плеера (Kodik, CVH, AniBoom и т.д.)
        url: Ссылка на видео-контент
        dubbing_id: Идентификатор озвучки
        dubbing_name: Название озвучки/переводчика

    Example:
        >>> player_part = PlayerPart(
        ...     title="Kodik",
        ...     url="//kodik.info/seria/1516908/...",
        ...     dubbing_id="12",
        ...     dubbing_name="AniMedia"
        ... )
    """

    title: str
    url: str
    dubbing_id: str
    dubbing_name: str


@dataclass
class Player:
    """
    Группировка видеоплееров по названию сервиса.

    Содержит все доступные варианты озвучек для конкретного
    видеоплеера.

    Attributes:
        title: Название сервиса видеоплеера
        ids: Список ID доступных озвучек для этого плеера
        players: Список конкретных плееров для каждой озвучки

    Example:
        >>> player = Player(
        ...     title="Kodik",
        ...     ids=[12, 46, 81],
        ...     players=[player_part1, player_part2, player_part3]
        ... )
    """

    title: str
    ids: List[int]
    players: List[PlayerPart]
    
    def __iter__(self):
        return iter(self.players)


@dataclass
class PlayerParseInfo:
    """
    Итоговая информация о всех видеоплеерах и озвучках аниме.

    Содержит полную информацию о доступных вариантах просмотра
    конкретного эпизода/серии аниме.

    Attributes:
        title: Название эпизода/серии
        all_dubbing: Список всех доступных ID озвучек
        all_players: Список всех доступных видеоплееров
        info: Детальная информация по каждому видеоплееру

    Example:
        >>> parse_info = PlayerParseInfo(
        ...     title="Атака титанов - Серия 1",
        ...     all_dubbing=[12, 46, 81],
        ...     all_players=["Kodik", "CVH", "AniBoom"],
        ...     info=[player1, player2, player3]
        ... )
    """

    title: str
    all_dubbing: List[int]
    all_players: List[str]
    info: List[Player]

    def __iter__(self):
        return iter(self.info)
    
    
@dataclass
class EmbedData:
    id: str
    domain: str
    
    duration: int # в секундах
    
    poster: str
    
    mpd_url: str
    m3u8_url: str
    
    quality: bool
    quality_video: int
    rating: str