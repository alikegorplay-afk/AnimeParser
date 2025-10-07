from dataclasses import dataclass
from typing import List

from core.models import BaseAnimeInfo


@dataclass
class AniBoomAnime(BaseAnimeInfo):
    """Класс для полной информации об аниме с сайта AnimeGo.
    
    Attributes:
        synonyms: (List[str]): Синонимы к название аниме
    
    Inherits:
        BaseMiniAnimeInfo: Все атрибуты родительского класса
        
    Notes:
        Требует реализации свойства ID в дочерних классах.
        Все характеристики организованы в виде списка AnimeRow для единообразия.
    
    Examples:
        >>> anime = BaseAnimeInfo(
        ...     title="Золотое божество 3",
        ...     url="https://animego.me/anime/zolotoe-bozhestvo-3-1632",
        ...     poster_url="https://example.com/poster.jpg",
        ...     description="После судьбоносных событий прошлого сезона Сугимо...",
        ...     anime_info=[
        ...         AnimeRow("Тип", "ТВ Сериал", original='<dl class="row"><dt class="col-6 col-sm-4 font-weight-norm...'),
        ...         AnimeRow("Эпизоды", 12, original='<dt class="col-6 col-sm-4 font-weig...')
        ...     ],
        ...      synonyms=[
        ...         "Золотой Камуй 3"
        ...     ]
        ... )
    """
    synonyms: List[str]
    
    def ID(self):
        return self.url.split('-')[-1]