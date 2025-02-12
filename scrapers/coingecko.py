import time, asyncio
import urllib.request
import urllib.error
import http.client
from contextlib import closing
from bs4 import BeautifulSoup

h = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'zstd',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'dnt': '1',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}


def fetch_url(url, retries=30):
    for attempt in range(retries):
        try:
            with closing(urllib.request.urlopen(url, timeout=20)) as response:
                return response.read()
        except http.client.IncompleteRead as e:
            print(f"Попытка {attempt + 1}: IncompleteRead ({len(e.partial)} bytes read) Coingecko")
            if attempt == retries - 1:
                return e.partial  # Возвращаем частичный результат
        except (urllib.error.URLError, http.client.HTTPException) as e:
            print(f"Ошибка: {e} Coingecko")
            if attempt == retries - 1:
                raise
        time.sleep(5)


def start():
    print('Coingecko starting')
    url = 'https://www.coingecko.com/?page=%d'
    page = 1
    while True:
        req = urllib.request.Request(url%page, headers=h)
        response = fetch_url(req)
        page += 1
        soup = BeautifulSoup(response, 'html.parser')
        pagin = soup.find('nav', {'class': 'gecko-pagination-nav'})

        token_list = soup.find('table', {'data-page': 'coinsIndex'}).tbody
        token_list = token_list.find_all('tr', {'class': 'tw-text-sm'})

        for token in token_list:
            token = token.find_all('td')[2].a
            name = token.find('div', {'class': 'tw-text-gray-700'})
            name, symbol = name.get_text('&&&', True).split('&&&')[:2]
            token_page = token.attrs['href']
            token_page = 'https://www.coingecko.com' + token_page
            req = urllib.request.Request(token_page, headers=h)
            response = fetch_url(req)
            time.sleep(2)
            soup = BeautifulSoup(response, 'html.parser')
            turl = soup.find('a', {'data-info-type': 'website'})
            if turl:
                turl = turl.attrs['href']
            yield [name, turl, token_page]

        pagin = pagin.find_all('span')[-1].a
        if not pagin:
            print('Coingecko finished')
            break
        
        time.sleep(2)
