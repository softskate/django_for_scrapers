from threading import Thread
import time
import os
import django

from scrapers import generator_functions

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webpanel.settings')
django.setup()

from utils import run


if __name__ == "__main__":
    while True:
        threads = [Thread(target=run, args=[func, generator_functions[func]], daemon=True) for func in generator_functions]
        for th in threads:
            th.start()

        for th in threads:
            th.join()

        print('Main thread finished. Sleeping')
        time.sleep(3600)

