import asyncio
import time

from collections import defaultdict
from pprint import pp
import httpx

from animego import AniBoom, AsyncAniBoom
from bs4 import BeautifulSoup

async def main():
    async with httpx.AsyncClient() as session:
        api = AniBoom()
        pp(api.get_info("https://animego.me/anime/beskonechnaya-gacha-2888"))
        
        #st = time.time()
        #for i in await asyncio.gather(*[asyncio.create_task(api.get_info("https://animego.me/anime/random")) for _ in range(10)]):
        #    print(i.url)
        #print(f"Работа программы: '{time.time() - st:.2f}' секунд!")
        

asyncio.run(main())