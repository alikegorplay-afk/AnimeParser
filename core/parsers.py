from abc import ABC, abstractmethod
from typing import List

from bs4 import BeautifulSoup, Tag, _IncomingMarkup

from .models import BaseAnimeInfo, AnimeRow, BaseMiniAnimeInfo
from .pagination import BasePagination

class BasicAnimeApi(ABC):
    def __init__(self, domen: str = 'https://animego.me', engine: str = 'html.parser'):
        self.domen = domen
        self.engine = engine
    
    @abstractmethod
    def get_info(self, url: str) -> BaseAnimeInfo:
        pass
    
    @abstractmethod
    def find_anime(self, url: str) -> BasePagination:
        pass

class BasicAnimeParserMini(ABC):
    def __init__(self, engine: str = 'html.parser'):
        self.engine: str = engine
    
    def parse_anime(self, html_code: _IncomingMarkup | BeautifulSoup) -> BaseMiniAnimeInfo:
        if not isinstance(html_code, (BeautifulSoup, Tag)):
            soup = BeautifulSoup(html_code, self.engine)
        else:
            soup = html_code
        
        return BaseMiniAnimeInfo(
            self._find_title(soup),
            self._find_poster(soup),
            self._find_url(soup)
        )
    
    @abstractmethod
    def _find_title(self, soup: BeautifulSoup) -> str: ...
    
    @abstractmethod
    def _find_poster(self, soup: BeautifulSoup) -> str: ...
    
    @abstractmethod
    def _find_url(self, soup: BeautifulSoup) -> str: ...   

class BasicAnimeParser(BasicAnimeParserMini):
    def __init__(self, engine: str = 'html.parser'):
        self.engine: str = engine
        
    def parse_anime(self, html_code: _IncomingMarkup) -> BaseAnimeInfo:
        soup = BeautifulSoup(html_code, self.engine)
        
        return BaseAnimeInfo(
            self._find_title(soup),
            self._find_url(soup),
            self._find_poster(soup),
            self._find_description(soup),
            self._find_info(soup)
        )   
    
    @abstractmethod
    def _find_info(self, soup: BeautifulSoup) -> List[AnimeRow]: ...
    
    @abstractmethod
    def _find_description(self, soup: BeautifulSoup) -> str: ...