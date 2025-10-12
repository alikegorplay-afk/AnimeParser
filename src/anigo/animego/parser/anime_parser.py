from bs4 import BeautifulSoup

from core.parsers import BasicAnimeParser, AnimeRow
from exceptions.utils import not_find
from ..models import AniBoomAnime


class AnimeBoomParser(BasicAnimeParser):
    """
    Парсер для извлечения информации об аниме с сайта AnimeBoom.

    Наследует от BasicAnimeParser и расширяет его функциональность
    для работы со специфической структурой сайта AnimeBoom.

    Args:
        engine (str): Движок для BeautifulSoup (по умолчанию 'html.parser').
        html (bool): Если True, сохраняет HTML-элементы в моделях данных.
    """

    def __init__(self, engine="html.parser", html: bool = False):
        """
        Инициализирует парсер AnimeBoom.

        Args:
            engine (str): Движок для BeautifulSoup ('html.parser', 'lxml', etc.).
            html (bool): Флаг сохранения HTML-элементов в данных.
        """
        self.html: bool = html
        super().__init__(engine)

    def parse_anime(self, html_code) -> AniBoomAnime:
        """
        Основной метод для парсинга страницы аниме.

        Args:
            html_code (str): HTML-код страницы аниме.

        Returns:
            AniBoomAnime: Объект с полной информацией об аниме.

        Raises:
            NotFound: Если не удается найти обязательные элементы на странице.
        """
        base_info = super().parse_anime(html_code)
        return AniBoomAnime(
            **base_info.__dict__,
            synonyms=self._find_synonyms(BeautifulSoup(html_code, self.engine)),
        )

    def _find_synonyms(self, soup: BeautifulSoup):
        """
        Ищет синонимы/альтернативные названия аниме.

        Args:
            soup (BeautifulSoup): Объект для парсинга HTML.

        Returns:
            list[str]: Список альтернативных названий аниме.

        Raises:
            NotFound: Если не удается найти блок с названием.
        """
        if not (title_box := soup.find("div", class_="anime-title")):
            raise not_find("title_box")
        return [i.get_text(strip=True) for i in title_box.find_all("li")]

    def _find_title(self, soup: BeautifulSoup):
        """
        Извлекает основное название аниме.

        Args:
            soup (BeautifulSoup): Объект для парсинга HTML.

        Returns:
            str: Основное название аниме.

        Raises:
            NotFound: Если не удается найти заголовок.
        """
        if not (title_box := soup.find("div", class_="anime-title")):
            raise not_find("title_box")
        if h1 := title_box.find("h1"):
            return h1.get_text(strip=True)
        raise not_find("h1")

    def _find_poster(self, soup: BeautifulSoup):
        """
        Ищет URL постера аниме.

        Args:
            soup (BeautifulSoup): Объект для парсинга HTML.

        Returns:
            str: URL изображения постера.

        Raises:
            NotFound: Если не удается найти блок с постером.
        """
        if not (poster_box := soup.find("div", class_="anime-poster")):
            raise not_find("poster_box")
        if not (img := poster_box.img):
            raise not_find("img")

        if not (src := img.get("srcset")):
            raise not_find("src")

        return src.split()[0]

    def _find_url(self, soup: BeautifulSoup):
        """
        Извлекает канонический URL страницы аниме.

        Args:
            soup (BeautifulSoup): Объект для парсинга HTML.

        Returns:
            str: Каноническая ссылка на страницу аниме.

        Raises:
            NotFound: Если не удается найти canonical link.
        """
        if link := soup.find("link", rel="canonical"):
            return link.get("href")
        raise not_find("link")

    def _find_description(self, soup: BeautifulSoup):
        """
        Извлекает описание аниме.

        Args:
            soup (BeautifulSoup): Объект для парсинга HTML.

        Returns:
            str: Текст описания аниме или пустая строка, если не найден.
        """
        if description := soup.find("div", class_="description"):
            return ' '.join(description.get_text().split())
        return ""

    def _find_info(self, soup: BeautifulSoup):
        """
        Извлекает дополнительную информацию об аниме (жанр, год выпуска и т.д.).

        Парсит структуру с определениями (dt) и описаниями (dd).

        Args:
            soup (BeautifulSoup): Объект для парсинга HTML.

        Returns:
            list[AnimeRow]: Список объектов с информацией об аниме.

        Note:
            FIXME: На данный момент обнаружена проблема при которой форматирование
                   текста не работает корректно для некоторых случаев.
        """
        info = []
        dt = [dt for dt in soup.find_all("dt") if dt.get_text(strip=True)]
        dd = [dd for dd in soup.find_all("dd") if dd.get_text(strip=True)]
        for dt, dd in zip(dt, dd):
            key = "".join(
                [
                    i.get_text(strip=True)
                    for i in dt.children
                    if len(i.get_text(strip=True)) > 1
                ]
            )
            value = [
                i.get_text(strip=True)
                for i in dd.children
                if len(i.get_text(strip=True)) > 1
            ]

            info.append(
                AnimeRow(
                    key,
                    "".join(value) if len(value) == 1 else value,  # Где то тут короче!
                    (dt, dd) if self.html else {key: value},
                )
            )
        return info
