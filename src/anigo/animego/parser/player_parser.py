from collections import defaultdict

from bs4 import BeautifulSoup, _IncomingMarkup

from ...exceptions.utils import not_find

from ..models import PlayerPart, Player, PlayerParseInfo


class PlayerParser:
    """
    Парсер для извлечения информации о видео-плеерах и озвучках аниме.

    Обрабатывает HTML-страницу с видеоплеерами и извлекает:
    - Название эпизода/серии
    - Список доступных озвучек (даббингов)
    - Информацию о видео-плеерах (Kodik, CVH, AniBoom и др.)
    - Ссылки на видео для каждой озвучки

    Attributes:
        engine (str): Движок для BeautifulSoup (по умолчанию 'html.parser')
    """

    def __init__(self, engine: str = "html.parser"):
        """
        Инициализирует парсер плееров.

        Args:
            engine (str): Движок для парсинга HTML ('html.parser', 'lxml', etc.)
        """
        self.engine = engine

    def parse_player(self, html_code: _IncomingMarkup) -> PlayerParseInfo:
        """
        Основной метод для парсинга страницы с видеоплеерами.

        Args:
            html_code (str | bytes): HTML-код страницы с видеоплеерами

        Returns:
            Player: Объект с информацией о плеерах и озвучках

        Raises:
            NotFound: Если не удается найти обязательные элементы на странице

        Example:
            >>> parser = PlayerParser()
            >>> player_info = parser.parse_player(html_code)
            >>> print(player_info.title)
            "Our Confession Story: The Experienced You and The Inexperienced Me"
        """
        soup = BeautifulSoup(html_code, self.engine)
        title = self._extract_title(soup)

        dubbing_data = self._parse_dubbing_data(soup)
        players_data = self._parse_players_data(soup)

        return self._build_player_object(title, players_data, dubbing_data)

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """
        Извлекает название эпизода/серии из HTML.

        Args:
            soup (BeautifulSoup): Объект для парсинга HTML

        Returns:
            str: Название эпизода или пустая строка если не найден
        """
        title_tag = soup.find("span", **{"data-episode-replace-title": True})
        return title_tag.get_text(strip=True) if title_tag else ""

    @staticmethod
    def _parse_dubbing_data(soup: BeautifulSoup) -> dict[str, str]:
        """
        Парсит блок с доступными озвучками (даббингами).

        Args:
            soup (BeautifulSoup): Объект для парсинга HTML

        Returns:
            dict[str, str]: Словарь {dubbing_id: dubbing_name}

        Raises:
            NotFound: Если блок с озвучками не найден
        """
        dubbing_box = soup.find("div", id="video-dubbing")
        if not dubbing_box:
            raise not_find("dubbing_box")

        return {
            tag.get("data-dubbing"): tag.get_text(strip=True)
            for tag in dubbing_box.children
            if tag.get_text(strip=True)
        }

    @staticmethod
    def _parse_players_data(soup: BeautifulSoup) -> dict[str, list[dict[str, str]]]:
        """
        Парсит блок с видеоплеерами и их ссылками.

        Args:
            soup (BeautifulSoup): Объект для парсинга HTML

        Returns:
            dict[str, list[dict[str, str]]]:
                Словарь {player_name: [{dubbing_id: video_url}]}

        Raises:
            NotFound: Если блок с плеерами не найден
        """
        players_box = soup.find("div", id="video-players")
        if not players_box:
            raise not_find("players_box")

        players = defaultdict(list)
        for player_tag in players_box.children:
            if player_tag.get_text(strip=True):
                players[player_tag.get_text(strip=True)].append(
                    {
                        player_tag.get("data-provide-dubbing"): player_tag.get(
                            "data-player"
                        )
                    }
                )
        return players

    @staticmethod
    def _build_player_object(
        title: str,
        players_data: dict[str, list[dict[str, str]]],
        dubbing_data: dict[str, str],
    ) -> PlayerParseInfo:
        """
        Создает итоговый объект Player из распарсенных данных.

        Args:
            title (str): Название эпизода
            players_data (dict): Данные о плеерах и ссылках
            dubbing_data (dict): Данные об озвучках

        Returns:
            PlayerParseInfo: Итоговый объект с информацией о плеерах
        """
        player_instances = PlayerParser._create_player_instances(
            players_data, dubbing_data
        )
        all_dubbing_ids = list(dubbing_data.keys())
        all_dubbing_title_ids = list(dubbing_data.values())

        return PlayerParseInfo(
            title=title,
            all_dubbing=[int(episode_id) for episode_id in all_dubbing_ids],
            all_players=all_dubbing_title_ids,
            info=player_instances,
        )

    @staticmethod
    def _create_player_instances(
        players_data: dict[str, list[dict[str, str]]], dubbing_data: dict[str, str]
    ) -> list[Player]:
        """
        Создает список объектов Player для каждого видеоплеера.

        Args:
            players_data (dict): Данные о плеерах
            dubbing_data (dict): Данные об озвучках

        Returns:
            list[Player]: Список объектов Player
        """
        return [
            PlayerParser._create_single_player(player_name, episodes_list, dubbing_data)
            for player_name, episodes_list in players_data.items()
        ]

    @staticmethod
    def _create_single_player(
        player_name: str,
        episodes_list: list[dict[str, str]],
        dubbing_data: dict[str, str],
    ) -> Player:
        """
        Создает объект Player для одного видеоплеера.

        Args:
            player_name (str): Название плеера (Kodik, CVH, etc.)
            episodes_list (list): Список словарей с ID озвучки и ссылками
            dubbing_data (dict): Данные об озвучках

        Returns:
            Player: Объект с информацией о конкретном плеере
        """
        player_parts = []
        episode_ids = []

        for episode_dict in episodes_list:
            episode_id, episode_url = next(iter(episode_dict.items()))
            episode_ids.append(episode_id)
            player_parts.append(
                PlayerPart(
                    title=player_name,
                    url=episode_url,
                    dubbing_id=int(episode_id),
                    dubbing_name=dubbing_data.get(episode_id),
                )
            )

        return Player(player_name, episode_ids, player_parts)
