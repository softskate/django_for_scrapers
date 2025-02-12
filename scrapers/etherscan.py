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
            print(f"Попытка {attempt + 1}: IncompleteRead ({len(e.partial)} bytes read) Etherscan")
            if attempt == retries - 1:
                return e.partial  # Возвращаем частичный результат
        except (urllib.error.URLError, http.client.HTTPException) as e:
            print(f"Ошибка: {e} Etherscan")
            if attempt == retries - 1:
                raise e
        time.sleep(5)


proxy = "http://P2j6nY5ZqsxtfCTwc9kB:RNW78Fm5@pool.infatica.io:10210"
proxy_handler = urllib.request.ProxyHandler({"http": proxy, "https": proxy})
opener = urllib.request.build_opener(proxy_handler)
urllib.request.install_opener(opener)

def start():
    print('Etherscan starting')
    url = 'https://etherscan.io/tokens?p=%d'
    page = 1
    while True:
        req = urllib.request.Request(url%page, headers=h)
        response = fetch_url(req)
        page += 1
        soup = BeautifulSoup(response, 'html.parser')
        pagin = soup.find('ul', {'class': 'pagination'})

        token_list = soup.find('tbody', {'class': 'align-middle'})
        token_list = token_list.find_all('tr')
        for token in token_list:
            token = token.find_all('td')[1].a
            name = token.find('div', {'class': 'hash-tag'}).get_text()
            token_page = token.attrs['href']
            token_page = 'https://etherscan.io' + token_page
            req = urllib.request.Request(token_page, headers=h)
            response = fetch_url(req)
            time.sleep(2)
            soup = BeautifulSoup(response, 'html.parser')
            try:
                turl = soup.find('div', {'id': 'ContentPlaceHolder1_divLinks'})
                if turl:
                    turl = turl.find('ul', {'aria-labelledby': 'dropdownMore2'})
                    turl = turl.a.attrs['href']
            except Exception as e:
                print('Error in etherscan:', e)
                turl = None
            yield[name, turl, token_page]

        pagin = pagin.find_all('li', {'class': 'page-item'})[-1]
        print(pagin.attrs['class'])
        if 'disabled' in pagin.attrs['class']:
            print('Etherscan finished')
            break
        
        time.sleep(2)
