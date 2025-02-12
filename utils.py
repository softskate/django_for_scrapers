from datetime import datetime, timezone
from urllib.parse import urlparse
from webapp.models import Website, ParserStatus, ParsedWebsite


def run(source, generator):
    try:
        parser_status, created = ParserStatus.objects.get_or_create(name=source)
        if not parser_status.enabled:
            return
        parser_status.status = 'running'
        parser_status.processed_items = 0
        parser_status.last_run = datetime.now(timezone.utc)
        parser_status.save()
        for name, url, token_page in generator():
            print([name, url], source)

            ParsedWebsite.objects.create(parser=parser_status, url=url)
            parser_status.processed_items += 1
            parser_status.last_scraped_page = token_page
            if parser_status.total_items < parser_status.processed_items:
                parser_status.total_items = parser_status.processed_items
            parser_status.save()

            if not parser_status.enabled:
                return

            if url:
                url = url.strip('/')
                if not url.startswith('http'):
                    url = 'https://'+url

            coin = Website.objects.filter(company=name).first()
            if not url:
                url = None
                if coin and coin.url:
                    continue
            
            if url and not url.startswith('http'):
                url = 'https://' + url
            domain = urlparse(url).netloc
            if not domain:
               url = None

            if coin:
                # if coin.domain == domain: continue
                pass

            else:
                coin = Website()
                coin.company = name

            coin.source = source
            coin.domain = domain
            coin.url = url
            coin.token_page = token_page
            coin.updated_at = datetime.now(timezone.utc)
            coin.save()

        # Завершение парсера
        if parser_status.total_items != parser_status.processed_items:
            parser_status.total_items = parser_status.processed_items
        parser_status.status = 'idle'
        parser_status.save()
    except Exception as e:
        print(f"Unknown error in [{generator}]: {e}", source)
