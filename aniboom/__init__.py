from urllib.parse import quote, urljoin

import httpx

from core.parsers import BasicAnimeApi

from .parser import AnimeBoomParser
from .pagination import AniBoomPagination


class AniBoom(BasicAnimeApi):
    def __init__(self, engine = 'html.parser', domen: str = 'https://animego.me'):
        super().__init__(domen, engine)
        self.aniboom = AnimeBoomParser(engine)
        
    def get_info(self, url: str):
        response = httpx.get(url, follow_redirects=True)
        response.raise_for_status()
        
        return self.aniboom.parse_anime(response.text)
    
    def find_anime(self, query: str):
        return AniBoomPagination._find(
            urljoin(self.domen, f"search/anime?q={quote(query)}&type=list&page={'{}'}"),
            self.engine
        )
        
    def find_manga(self, query: str):
        return AniBoomPagination._find(
            urljoin(self.domen, f"search/manga?q={quote(query)}&type=list&page={'{}'}"),
            self.engine
        )
        
    def find_people(self, query: str):
        return AniBoomPagination._find(
            urljoin(self.domen, f"search/people?q={quote(query)}&type=list&page={'{}'}"),
            self.engine
        )