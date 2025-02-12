import time, asyncio
import requests
from bs4 import BeautifulSoup

h = {
    'accept': 'application/json',
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
    print('Icodrops starting')
    url = 'https://icodrops.com/category/active-ico/filter/?page=%d'
    page = 1
    while True:
        d = requests.get(url%page, headers=h)
        d = d.json()
        page += 1
        soup = BeautifulSoup(d['rendered_html'], 'html.parser')
        token_list = soup.find_all('li', {'class': 'Tbl-Row'})

        for token in token_list:
            name = token.find('p', {'class': 'Cll-Project__name'}).get_text().strip()
            token_page = 'https://icodrops.com' + token.a.attrs['href']
            td = requests.get(token_page, headers=h)
            time.sleep(2)
            
            soup = BeautifulSoup(td.content, 'html.parser')
            try:
                turl = soup.find('ul', {'class': 'Project-Page-Header__links-list'}).a.attrs['href']
            except Exception as e:
                print('Error in icodrops:', e)
                turl = None
            yield [name, turl, token_page]
            

        if d['current_page'] == d['total_pages']:
            print('Icodrops finished')
            break
        
        time.sleep(2)
