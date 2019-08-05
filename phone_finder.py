import asyncio
import re
from lxml import html
from aiohttp import ClientSession
from lxml.html import HtmlElement


phone_re = re.compile(r'(?P<country_code>\+7|8)?\s*[\(\-]?(?P<code>\d{3})?[\)\-]?\s*(?P<number>[\d \-]{7,10})')


def search_in_html(html_content):
    """
    Поиск телефонных номеров на html странице
    """
    if not html_content:
        return []

    doc: HtmlElement = html.fromstring(html_content)

    text = doc.xpath("body//text()[not(ancestor::script)]")

    # ищем регулярным выражением и отфильтровываем из номеров все пробелы и дефисы
    phones = [(m.group(0), m.group('code'), m.group('number').translate(str.maketrans('', '', ' \n-')))
              for match in (re.finditer(phone_re, t) for t in text if t.strip())
              for m in match]

    # отфильтровываем числа неявляющиеся номерами телефонов (даты и т. д.)
    return list(set([f'+7{phone[1] or "495"}{phone[2]}' for phone in phones if len(phone[2]) == 7]))


async def fetch_page(url: str, session: ClientSession):
    """
    Загружает страницу

    """
    async with session.get(url) as response:
        if response.status == 200:
            return await response.read()
        else:
            return ''


async def search_on_page(url: str, session) -> list:
    """
    Поиск номеров телефонов в html страницы

    """
    html_content = await fetch_page(url, session)

    return search_in_html(html_content)


def search_for_phones(urls: list):
    """
    Поиск телефонных номеров на заданых в urls веб-страницах

    """
    phones = [[]]

    async def _run():
        async with ClientSession() as session:
            phones.extend(await asyncio.gather(
                *[asyncio.ensure_future(search_on_page(url, session)) for url in urls]
            ))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.ensure_future(_run())
    )

    return [phone
            for phone_list in phones
            for phone in phone_list]
