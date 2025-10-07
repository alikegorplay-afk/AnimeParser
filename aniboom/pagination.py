from math import ceil

import httpx

from bs4 import BeautifulSoup

from .parser import AnimeBoomPageParser

from core.pagination import BasePagination, BaseMiniAnimeInfo
from exceptions.utils import not_find

class AniBoomPagination(BasePagination):
    MAX_ANIME_IN_PAGE = 16
    
    def __init__(self, url, engine = 'html.parser', *args, **kwargs):
        super().__init__(url, engine, *args, **kwargs)
        self.parser = AnimeBoomPageParser(self.engine)
    
    def fetch(self, url, *args, **kwargs):
        response = httpx.get(
            url.format(self.current_page),
            *args, **kwargs
        )
        response.raise_for_status()
        return response.text
    
    def parse_anime(self, html_code):
        soup = BeautifulSoup(html_code, self.engine)
        if not (all_anime := soup.find_all("div", class_="animes-grid-item")):
            raise not_find('all_anime')
        return [self.parser.parse_anime(anime) for anime in all_anime]

    @classmethod
    def _find(cls, url: str, engine: str,  *args, **kwargs):
        cls = cls(url, engine, *args, **kwargs)
        html = cls.fetch(url)
        soup = BeautifulSoup(html, engine)
        try:
            cls.max_page = ceil(int(soup.find("span", class_="search-county").get_text(strip=True)) / cls.MAX_ANIME_IN_PAGE)
            cls.cache[cls.current_page] = cls.parse_anime(html)
        except AttributeError:
            raise ValueError(f"Не был найден ни один тайтл по URL: {url}")
        
        return cls
    
    def __iter__(self):
        for page in range(1, self.max_page + 1):
            yield self.select_page(page)