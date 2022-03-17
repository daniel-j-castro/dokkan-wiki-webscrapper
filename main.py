from bs4 import BeautifulSoup
import requests

"""
Information regarding a unit is under a div with class=mw-parser-output, this div has a different number of children 
depending on whether a unit is a tranforming/exchange/fusion/etc. unit so it is important to make a distinction
in order to pull all the information regarding the unit.
"""
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
all_info = soup.find('div', class_ ='mw-parser-output')
print(tab_check(all_info))

"""
ignore first child grab rest for units with multiple info
"""
count = 0
for x in all_info.find('div', class_="tabber wds-tabber").children:
    count +=1
print(count)
