import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytest
import httpx

from bs4 import BeautifulSoup

from src.animego import AniBoom

api = AniBoom()

@pytest.mark.parametrize(
    "url, result",
    [
        ("https://animego.me/anime/vanpanchmen-s1-11", "Ванпанчмен"),
        ("https://animego.me/anime/vanpanchmen-2-12", "Ванпанчмен 2"),
        ("https://animego.me/anime/vanpanchmen-speshly-13", "Ванпанчмен: Спешлы"),
        ("https://animego.me/anime/vanpanchmen-put-k-stanovleniyu-geroem-14", "Ванпанчмен: Путь к становлению героем"),
        ("https://animego.me/anime/chernyy-klever-27", "Чёрный клевер"),
    ]
)
def test_get_info(url, result):
    assert api.get_info(url).title == result


@pytest.mark.parametrize(
    "url, result",
    [
        ("https://animego.me/anime/vanpanchmen-s1-11", "11"),
        ("https://animego.me/anime/vanpanchmen-2-12", "12"),
        ("https://animego.me/anime/vanpanchmen-speshly-13", "13"),
        ("https://animego.me/anime/vanpanchmen-put-k-stanovleniyu-geroem-14", "14"),
        ("https://animego.me/anime/chernyy-klever-27", "27"),
    ]
)
def test_id(url, result):
    assert api.get_info(url).ID == result


def test_description():
    assert api.get_info("https://animego.me/anime/vanpanchmen-s1-11").description == """Мы все привыкли, что комиксы наполнены различными злодеями, безумцами с планом захвата планеты и прочими неприятностями. Город Зет-Сити уже давно привык к такому роду событий, постоянными захватчиками из других миров и прочими бедствиями. Самое важное, чтобы всегда вовремя появился супергерой, которой справится со всеми проблемами и сможет победить всех злодеев. Таким является парень по имени Сайтама. Вот только он выбивается из общего фона в жизни типичного города из комикса. Он невысокий, не может вести себя достаточно пафосно и не говорит высокопарных речей. Более того, внешний вид нашего героя состоит из простой одежды, а на голове нет ни одной волосинки.В прошлом Сайтама был обычным человеком, который потерял свою работу. Только благодаря своему терпению и постоянным тренировкам он смог за три года стать самым сильным в мире. Чтобы победить врага, ему достаточно все лишь один раз ударить соперника, как тот окажется поверженным. Вот только теперь у него серьезная проблема – нет достойных соперников, и теперь вся это супергеройская жизнь превратилась для него в настоящую рутину."""

#api.get_info()