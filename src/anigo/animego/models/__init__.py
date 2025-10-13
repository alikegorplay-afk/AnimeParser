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
    all_dubbing: List[str]
    all_players: List[str]
    info: List[Player]

    def __iter__(self):
        return iter(self.info)
    
    
@dataclass
class EmbedData:
    """
    Данные для встраивания видео-плеера.

    Содержит техническую информацию о видео-контенте
    для воспроизведения через MPD/HLS протоколы.

    Attributes:
        id: Уникальный идентификатор видео
        domain: Домен источника видео
        duration: Длительность видео в секундах
        poster: URL постера/превью видео
        mpd_url: URL MPD-манифеста (MPEG-DASH)
        m3u8_url: URL M3U8-плейлиста (HLS)
        quality: Флаг доступности качества видео
        quality_video: Числовое значение качества (например, 1080)
        rating: Рейтинг видео (возможно, возрастной рейтинг)

    Example:
        >>> embed = EmbedData(
        ...     id="video_12345",
        ...     domain="example.com",
        ...     duration=1440,
        ...     poster="https://example.com/poster.jpg",
        ...     mpd_url="https://example.com/video.mpd",
        ...     m3u8_url="https://example.com/video.m3u8",
        ...     quality=True,
        ...     quality_video=1080,
        ...     rating="R"
        ... )
    """
    id: str
    domain: str
    duration: int  # в секундах
    poster: str
    mpd_url: str
    m3u8_url: str
    quality: bool
    quality_video: int
    rating: str

@dataclass
class CvhItems:
    """
    Элемент видео-контента из CVH API.

    Представляет отдельную серию/сезон с мета-информацией
    о локализации и техническими параметрами.

    Attributes:
        cvh_id: Уникальный идентификатор в системе CVH
        name: Название элемента (обычно пустое)
        vk_id: Идентификатор связанного VK контента
        voice_studio: Студия озвучки
        voice_type: Тип озвучки (дубляж, многоголосый, и т.д.)
        season: Номер сезона
        episode: Номер эпизода

    Example:
        >>> cvh_item = CvhItems(
        ...     cvh_id="cvh_67890",
        ...     name="",
        ...     vk_id="vk_54321",
        ...     voice_studio="AniLibria",
        ...     voice_type="multi",
        ...     season=1,
        ...     episode=5
        ... )
    """
    cvh_id: str
    name: str  # Обычно пустой
    vk_id: str
    voice_studio: str
    voice_type: str
    season: int
    episode: int


@dataclass
class CvhData:
    """
    Основная структура данных видео-контента от CVH API.

    Содержит общую информацию о видео и список всех
    доступных элементов (серий/сезонов).

    Attributes:
        title: Название видео-контента
        isSerial: Флаг, указывающий что это сериал (True) или фильм (False)
        items: Список всех доступных видео-элементов

    Example:
        >>> cvh_data = CvhData(
        ...     title="Атака титанов",
        ...     isSerial=True,
        ...     items=[cvh_item1, cvh_item2, cvh_item3]
        ... )
    """
    title: str
    is_serial: bool
    items: List[CvhItems]