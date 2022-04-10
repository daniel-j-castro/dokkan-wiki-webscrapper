from bs4 import BeautifulSoup
import requests
from os import path

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
        left_info = handle_left(left_table, header_info['unit_id']) 
    else:
        for x in unit.find('div', class_="tabber wds-tabber").children:
           header = x.find('table')
           left_table = x.find('div', class_='lefttablecard')
           if header == None:
               continue
           header_info = handle_header(header)
           left_info = handle_left(left_table, header_info['unit_id'])


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
    if '/' in header_info['max_lvl']:
        header_info['max_lvl'] = header_info['max_lvl'].split('/')[1]
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
    if not path.exists('./thumbs/'+header_info['unit_id']+'.png'):
        image = header.find('img')
        if 'data-src' in image.attrs:
            img = requests.get(image['data-src'])
        else:
            img = requests.get(image['src'])
        with open('./thumbs/'+header_info['unit_id']+'.png', 'wb') as f:
            f.write(img.content)
    
    return header_info

def handle_left(left_card, uid) -> dict:
    #Grab unit's art
    if not path.exists('./art/'+uid+'.png'):
        image = left_card.find('table').find('img')
        if 'data-src' in image.attrs:
            img = requests.get(image['data-src'])
        else:
            img = requests.get(image['src'])
        with open('./art/'+uid+'.png', 'wb') as f:
            f.write(img.content)
    #Info is separated into tables on page
    left_tables = left_card.find_all('table')
    #Grabbing unit release date
    rows = left_tables[2].find_all('tr')
    #Determine if the unit is released on both versions
    if len(rows) > 2:
        jp_cols = rows[1].find_all('td')
        #Determine if the unit has an EZA
        jp = jp_cols[0].find('img')['alt'].split()[0]
        global_cols = rows[2].find_all('td')
        glb = global_cols[0].find('img')['alt'].split()[0]
        if(len(jp_cols) > 2):
            release_date = {jp:{'Release':jp_cols[1].text, 'EZA':jp_cols[2].text}}
            release_date[glb] = {'Release':global_cols[1].text, 'EZA':global_cols[2].text}
        else:
            release_date = {jp:{'Release':jp_cols[1].text}}
            release_date[glb] = {'Release':global_cols[1].text}
        print(release_date)
    else:
        cols = rows[1].find_all('td')
        region = cols[0].find('img')['alt'].split()[0]
        if(len(cols) > 2):
            release_date = {region:{'Release':cols[1].text, 'EZA':cols[2].text}}
        else:
            release_date = {region:{'Release':cols[1].text}}
        print(release_date)
        
    



html_response = requests.get('https://dbz-dokkanbattle.fandom.com/wiki/The_Captain%27s_Trump_Card_Captain_Ginyu').text
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
