import json

from bs4 import BeautifulSoup

from ...exceptions import DataIncorrectError, not_find

class MpdParser:
    """Парсер HTML страниц для извлечения видео данных"""
    
    def __init__(self, engine: str):
        self.engine = engine
        
    def parse_aniboom_html(self, html_content: str) -> dict:
        """Парсит HTML страницу и извлекает параметры видео"""
        soup = BeautifulSoup(html_content, self.engine)
        data_block = soup.find("div", id="video")
        
        if not data_block:
            raise not_find('"div", id="video"')
        
        data_parameters = data_block.get('data-parameters')
        if not data_parameters:
            raise not_find('data_parameters')
        
        try:
            return json.loads(data_parameters)
        except json.JSONDecodeError as e:
            raise DataIncorrectError(f"Данные не корректны: {str(e)}") from e
        
    def parse_mpd(self, data: str):
        soup = BeautifulSoup(data, 'xml')
        print(soup.find('SegmentTemplate').get("media"))