from bs4 import BeautifulSoup
import requests


def tab_check(unit) -> str:
    count = 0
    for x in unit.children:
        count += 1
    if count > 10:
        return "n"
    else:
        return "y"

html_response = requests.get('https://dbz-dokkanbattle.fandom.com/wiki/Boiling_Power_Super_Saiyan_Goku').text
soup = BeautifulSoup(html_response, 'lxml')
right = soup.find('div', class_ ='mw-parser-output')
print(type(right))
print(tab_check(right))