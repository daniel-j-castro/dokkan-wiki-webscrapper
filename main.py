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

def grab_unit_info(unit):
    if tab_check(unit) == "n":
        header = unit.find('table')
        right_table = unit.find('div', class_='righttablecard')
        left_table = unit.find('div', class_='lefttablecard')
        header_info = handle_header(header)      
        print(header_info)
    else:
        header = unit.find('table')
        header_info = handle_header(header)
        print(header_info)

"""
Grab all relevant information in the header table of a unit.
Returns a Dictonary
"""
def handle_header(header) -> dict:
    header_info = {'unit_title': None, 'unit_name': None, 'max_lvl': None, 'sa': None, 'rarity': None, 'unit_type': None,
                   'unit_class': None, 'unit_cost': None, 'unit_id': None}
    #Separate Table Rows (second row irrelevant)
    rows = header.find_all('tr')
    first_row_info = rows[0].find_all('td')
    third_row_info = rows[2].find_all('td')
    #Grabbing Name of Unit
    needed_info = str(first_row_info[1].find('b')).split('<br/>')
    header_info['unit_title'] = needed_info[0].split('<b>')[1].replace('&amp; ', '')
    header_info['unit_name'] = needed_info[1].split('</b>')[0].replace('&amp; ', '')
    #Grabbing Max LVL of unit
    header_info['max_lvl'] = third_row_info[0].text
    #Grabbing SA LVL
    header_info['sa'] = third_row_info[1].text.split('/')[1]
    #Grabbing rarity
    header_info['rarity'] = third_row_info[2].find('a')['href'].split(':')[1]
    #Grabbing type and class
    unit_type = third_row_info[3].find_all('a')
    if(len(unit_type) > 1):
        header_info['unit_class'], header_info['unit_type'] = unit_type[1]['href'].split(':')[1].split('_')
    else:
        header_info['unit_class'], header_info['unit_type'] = unit_type[0]['href'].split(':')[1].split('_')
    #Grabbing cost
    header_info['unit_cost'] = third_row_info[4].text
    if '/' in header_info['unit_cost']:
       header_info['unit_cost'] = header_info['unit_cost'].split('/')[0]
    #Grabbing ID of unit
    header_info['unit_id'] = third_row_info[5].text

    #Download thumb of unit
    image = header.find('img')
    if 'data-src' in image.attrs:
        img = requests.get(image['data-src'])
    else:
        img = requests.get(image['src'])
    with open('./thumbs/'+header_info['unit_id']+'.png', 'wb') as f:
        f.write(img.content)
    
    return header_info


html_response = requests.get('https://dbz-dokkanbattle.fandom.com/wiki/Ultimate_Power_Saiyan_Warriors_Super_Saiyan_4_Goku_%26_Super_Saiyan_4_Vegeta').text
soup = BeautifulSoup(html_response, 'lxml')
all_info = soup.find('div', class_ ='mw-parser-output')
check = tab_check(all_info)

"""
ignore first child grab rest for units with multiple info
"""
count = 0
if check == 'y':
    for x in all_info.find('div', class_="tabber wds-tabber").children:
        count +=1

grab_unit_info(all_info)
