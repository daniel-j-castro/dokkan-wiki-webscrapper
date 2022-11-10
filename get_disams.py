from bs4 import BeautifulSoup
import requests

BASE_URL = 'https://dbz-dokkanbattle.fandom.com'

def get_disams() -> list:
    html_response = requests.get('https://dbz-dokkanbattle.fandom.com/wiki/Disambiguation').text
    soup = BeautifulSoup(html_response, 'lxml')
    tabber = soup.find(class_='tabber wds-tabber')
    tabs = tabber.children
    next(tabs)
    disams = []
    links = []
    for x in tabs:
        links.append(x.find_all('a'))
    for result in links:
        for x in result:
            if 'disambiguation' in x['href']:
                disams.append(BASE_URL + x['href'])
    return disams

if __name__ == '__main__':
    print(get_disams())