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
    print('Cryptorank starting')
    url = 'https://api.cryptorank.io/v0/coins/v2?locale=en&lifeCycle=traded'
    d = requests.get(url, headers=h)
    token_list = d.json()
    for token in token_list['data']:
        name = token['name']
        token_page = 'https://cryptorank.io/price/' + token['key']
        for _ in range(5):
            d = requests.get(token_page, headers=h)
            time.sleep(2)
            
            soup = BeautifulSoup(d.content, 'html.parser')
            token_data = soup.find('script', {'id': '__NEXT_DATA__'})
            if token_data: break
        else:
            continue
        
        token_data = json.loads(token_data.get_text())
        token_data = token_data['props']['pageProps']
        turl = None
        if 'coin' in token_data:
            token_data = token_data['coin']
            
        name = token_data['name']
        for link in token_data['links']:
            if link['type'] == 'web':
                turl = link['value']
                break
        yield [name, turl, token_page]

    print('Cryptorank finished')
