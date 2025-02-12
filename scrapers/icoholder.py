import json
import time, asyncio
import requests
from bs4 import BeautifulSoup

h = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'dnt': '1',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://icoholder.com/en/cryptos',
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
def start():
    print('Icoholder starting')
    url = 'https://icoholder.com/en/cryptos?sort=q.market_cap&direction=desc'
    while True:
        d = requests.get(url, headers=h)
        soup = BeautifulSoup(d.content, 'html.parser')

        token_list = soup.find('div', {'class': 'endless-list'})
        token_list = token_list.find_all('div', {'class': 'position-relative'})

        for token in token_list:
            token_page = 'https://icoholder.com' + token.attrs['data-direct']
            d = requests.get(token_page, headers=h)
            time.sleep(2)
            soup = BeautifulSoup(d.content, 'html.parser')
            token_data = soup.find('script', {'type': 'application/ld+json'})
            if token_data:
                token_data = json.loads(token_data.get_text())
                name = token_data['name']
                turl = token_data['url']
                yield [name, turl, token_page]
        
        pagin = soup.find('ul', {'class': 'pagination'})
        if pagin:
            pagin = pagin.find_all('li')[-1]
            
        if not pagin or pagin.attrs.get('class') == ['disabled']:
            print('Icoholder finished')
            break

        url = 'https://icoholder.com' + pagin.a.attrs['href']
        time.sleep(2)
