from typing import Dict

import httpx

from bs4 import BeautifulSoup, Tag

class Player:
    def __init__(self, domen: str = 'https://animego.me', engine: str = 'html.parser'):
        self.base_headers: Dict[str, str] = {
            'referer': 'https://animego.me',
            'x-requested-with': 'XMLHttpRequest',
        }
        self.engine = engine
        self.domen = domen

    def get_info(self, id: str | int):
        data: Dict[str, str] = self.fetch(f'https://animego.me/anime/{id}/player', 'get', headers = self.base_headers)
        if data.get('status') != 'success':
            # NOTE: Поменять на StatusError
            raise AttributeError(f"Неожиданный статус ответа: {data.get('status')}")
        elif not (html_code := data.get('content')):
            # NOTE: Поменять на NotFindError
            raise AttributeError("Не был обнаружен 'content'")
        
        with open('test.html', 'w', encoding='utf-8') as file:
            file.write(html_code)
        
        soup = BeautifulSoup(html_code, self.engine)
        
        
    def fetch(self, url: str, method: str = 'GET', *args, **kwargs):
        response = httpx.request(method, url, *args, **kwargs)
        response.raise_for_status()

        return response.json()
    
player = Player()
player.get_info(2868)