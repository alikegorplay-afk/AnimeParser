import asyncio

from pprint import pp
import httpx

from aniboom_async import AsyncAniBoom


async def main():
    async with httpx.AsyncClient() as session:
        api = AsyncAniBoom(session)
        result = await api.find_anime("я стал")
        async for i in result:
            print(i)
        print(result)

asyncio.run(main())