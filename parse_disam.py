import pymongo
from bs4 import BeautifulSoup
import os
import requests

BASE_URL = 'https://dbz-dokkanbattle.fandom.com'

def load_cache() -> set:
    cache = set()
    with open('cache.txt', 'r') as f:
        cache_items = f.readlines()
    for item in cache_items:
        cache.add(item)
    return cache

def parse_disambiguation(disambiguation_page) -> list:
    cache = load_cache()
    print(cache)
    html_response = requests.get(disambiguation_page).text
    soup = BeautifulSoup(html_response, 'lxml')
    table = soup.find_all('table')[1]
    links = table.find_all('a', {'title': re.compile(r".*")})
    cleansed_links = [BASE_URL + x['href'] for x in links if 'Extreme_Z-Awakened' 
                                 not in x['href'] or x['href'] in cache]
    for link in cleansed_links:
        print(link)
    return cleansed_links

if __name__ == "__main__":
    parse_disambiguation('https://dbz-dokkanbattle.fandom.com/wiki/Pan_(disambiguation)#Pan_(GT)')