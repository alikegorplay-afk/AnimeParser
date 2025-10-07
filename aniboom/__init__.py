import httpx

from core.parsers import BasicAnimeApi

from .parser import AnimeBoomParser
from .pagination import AniBoomPagination


class AniBoom(BasicAnimeApi):
    def __init__(self, engine = 'html.parser'):
        super().__init__(engine)
        self.aniboom = AnimeBoomParser(engine)
        
    def get_info(self, url: str):
        response = httpx.get(url, follow_redirects=True)
        response.raise_for_status()
        
        return self.aniboom.parse_anime(response.text)
    
    def find_anime(self, query: str):
        return AniBoomPagination._find(
            f'https://animego.me/search/anime?q={query.replace(' ', '%20')}&type=list&page={'{}'}',
            self.engine
        )
        
    def find_manga(self, query: str):
        return AniBoomPagination._find(
            f'https://animego.me/search/manga?q={query.replace(' ', '%20')}&type=list&page={'{}'}',
            self.engine
        )
        
    def find_people(self, query: str):
        return AniBoomPagination._find(
            f'https://animego.me/search/people?q={query.replace(' ', '%20')}&type=list&page={'{}'}',
            self.engine
        )