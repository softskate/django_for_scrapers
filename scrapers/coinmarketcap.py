import json
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
    print('Coinmarketcap starting')
    url = 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing?start=%d&limit=100&sortBy=rank&sortType=desc&convert=USD,BTC,ETH&cryptoType=all&tagType=all&audited=false&aux=ath,atl,high24h,low24h,num_market_pairs,cmc_rank,date_added,max_supply,circulating_supply,total_supply,volume_7d,volume_30d,self_reported_circulating_supply,self_reported_market_cap'
    offset = 1
    while True:
        d = requests.get(url%offset, headers=h)
        open('tmp1.json', 'wb').write(d.content)
        offset += 100
        data = d.json()

        for token in data['data']['cryptoCurrencyList']:
            name = token['name']
            pl = {"cryptoId": token['id']}
            token_page = 'https://api.coinmarketcap.com/gravity/v3/gravity/announcement/query'
            d = requests.post(token_page, json=pl, headers=h)
            token_page = 'https://coinmarketcap.com/currencies/' + token['slug']
            turl = None
            if d.status_code == 200:
                tdata = d.json()
                turl = None
                if 'owner' in tdata['data']:
                    turl = tdata['data']['owner'].get('websiteLink')

            if not turl:
                d = requests.get(token_page, headers=h)
                soup = BeautifulSoup(d.content, 'html.parser')
                tdata = soup.find('script', {'id': '__NEXT_DATA__'})
                tdata = json.loads(tdata.get_text())

                turl = tdata['props']['pageProps']['detailRes']['detail']['urls']['website']
                turl = turl[0] if turl else None

            time.sleep(2)
            yield [name, turl, token_page]

        if offset > int(data['data']['totalCount']):
            print('Coinmarketcap finished')
            break
        
        time.sleep(2)
