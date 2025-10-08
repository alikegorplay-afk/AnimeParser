from core.parsers import BasicAnimeParserMini
from exceptions.utils import not_find


class AnimeBoomPageParser(BasicAnimeParserMini):
    """
    Парсер для страниц со списками аниме на AnimeBoom.

    Используется для извлечения базовой информации из карточек аниме
    в разделах типа "Популярные", "Новые", "Поиск" и т.д.

    Наследует от BasicAnimeParserMini и реализует специфичные для AnimeBoom
    методы поиска элементов.

    Example:
        >>> parser = AnimeBoomPageParser()
        >>> anime_cards = parser.parse_anime_list(html_code)
        >>> for anime in anime_cards:
        ...     print(f"{anime.title} - {anime.url}")
    """

    def __init__(self, engine: str = "html.parser"):
        """
        Инициализирует парсер страниц со списками аниме.

        Args:
            engine (str): Движок для BeautifulSoup ('html.parser', 'lxml', etc.)
        """
        super().__init__(engine)

    def _find_title(self, soup) -> str:
        """
        Извлекает название аниме из карточки.

        Args:
            soup (BeautifulSoup): Объект для парсинга HTML карточки аниме

        Returns:
            str: Название аниме

        Raises:
            NotFound: Если элемент с названием не найден
        """
        if title := soup.find("div", class_="h5"):
            return title.get_text(strip=True)
        raise not_find("title")

    def _find_poster(self, soup) -> str:
        """
        Извлекает URL постера аниме.

        Args:
            soup (BeautifulSoup): Объект для парсинга HTML карточки аниме

        Returns:
            str: URL изображения постера

        Raises:
            NotFound: Если элемент с постером не найден
        """
        if poster := soup.find("div", class_="anime-grid-lazy"):
            return poster.get("data-original")
        raise not_find("poster")

    def _find_url(self, soup) -> str:
        """
        Извлекает ссылку на страницу аниме.

        Args:
            soup (BeautifulSoup): Объект для парсинга HTML карточки аниме

        Returns:
            str: URL страницы аниме

        Raises:
            NotFound: Если ссылка не найдена
        """
        if url := soup.find("a", class_="d-block"):
            return url.get("href")
        raise not_find("url")
