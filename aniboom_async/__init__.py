from urllib.parse import quote, urljoin

import httpx

from core.parsers import BasicAnimeApi

from .parser import AnimeBoomParser
from .pagination import AsyncAniBoomPagination


class AsyncAniBoom(BasicAnimeApi):
    def __init__(self, session: httpx.AsyncClient, engine = 'html.parser', domen: str = 'https://animego.me'):
        super().__init__(domen, engine)
        self.aniboom = AnimeBoomParser(engine)
        self.session = session
        
    async def get_info(self, url: str):
        response = await self.session.get(url, follow_redirects=True)
        response.raise_for_status()
        
        return self.aniboom.parse_anime(response.text)
    
    async def find_anime(self, query: str):
        return await AsyncAniBoomPagination._find(
            urljoin(self.domen, f"search/anime?q={quote(query)}&type=list&page={'{}'}"),
            self.session,
            self.engine
        )
        
    async def find_manga(self, query: str):
        return await AsyncAniBoomPagination._find(
            urljoin(self.domen, f"search/manga?q={quote(query)}&type=list&page={'{}'}"),
            self.session,
            self.engine
        )
        
    async def find_people(self, query: str):
        return await AsyncAniBoomPagination._find(
            urljoin(self.domen, f"search/people?q={quote(query)}&type=list&page={'{}'}"),
            self.session,
            self.engine
        )