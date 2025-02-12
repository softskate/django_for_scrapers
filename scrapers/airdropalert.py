import time, asyncio
import requests
from bs4 import BeautifulSoup

h = {
    'accept': 'text/html,application/json,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
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
    print('Airdropalert starting')
    url = 'https://airdropalert.com/wp-admin/admin-ajax.php?draw=1&columns%5B0%5D%5Bdata%5D=rank&columns%5B0%5D%5Bname%5D=rank&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=name&columns%5B1%5D%5Bname%5D=name&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=price_usd&columns%5B2%5D%5Bname%5D=price_usd&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=market_cap_usd&columns%5B3%5D%5Bname%5D=market_cap_usd&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=volume_usd_24h&columns%5B4%5D%5Bname%5D=volume_usd_24h&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=available_supply&columns%5B5%5D%5Bname%5D=available_supply&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=percent_change_24h&columns%5B6%5D%5Bname%5D=percent_change_24h&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B7%5D%5Bdata%5D=weekly&columns%5B7%5D%5Bname%5D=weekly&columns%5B7%5D%5Bsearchable%5D=true&columns%5B7%5D%5Borderable%5D=true&columns%5B7%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B7%5D%5Bsearch%5D%5Bregex%5D=false&start={offset}&length=100&search%5Bvalue%5D=&search%5Bregex%5D=false&action=coinmc_table&id=294564&watchlist=false&restrict=true&currency=USD&_={now}'
    offset = 1
    while True:
        d = requests.get(url.format(offset=offset, now=int(time.time()*1000)), headers=h)
        offset += 100
        data = d.json()

        for token in data['data']:
            token = token['name']
            name = token.split('coin-name">')[1].split('</div>')[0]
            
            token_page = token.split('<a href="')[1].split('" class="coin-title">')[0]
            d = requests.get(token_page, headers=h)
            time.sleep(2)

            soup = BeautifulSoup(d.content, 'html.parser')
            turl = soup.find('ul', {'class': 'coinmc-links'})
            if turl and turl.a:
                turl = turl.a.attrs['href']

            yield [name, turl, token_page]

        if offset >= data['recordsFiltered']:
            print('Airdropalert finished')
            break

        time.sleep(2)
