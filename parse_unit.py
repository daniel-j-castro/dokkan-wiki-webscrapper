from bs4 import BeautifulSoup
import requests
from os import path
import os
from dotenv import load_dotenv
import boto3
import re
import pymongo

load_dotenv()
access_key = os.getenv('ACCESS_KEY')
secret_key = os.getenv('SECRET_KEY')
bucket_name = os.getenv('BUCKET_NAME')
mongo_uri = os.getenv('MONGO_URI')

try:
    connection = pymongo.MongoClient(mongo_uri)
    db = connection['dokkan-api']
    unit_collection = db['unit_details']
except:
    print('something went wrong with connection')

client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
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
    cards = {}
    if tab_check(unit) == "n":
        header = unit.find('table')
        right_table = unit.find('div', class_='righttablecard')
        left_table = unit.find('div', class_='lefttablecard')
        potential_eza = unit.find('div', attrs={'style':'float:left; width:100%;'})
        header_info = handle_header(header)     
        left_info = handle_left(left_table, header_info['unit_id']) 
        right_info = handle_right(right_table, potential_eza)
        print('done')
        header_info.update(left_info)
        header_info.update(right_info)
        cards[header_info['unit_id']] = header_info 
    else:
        children = unit.find('div', class_="tabber wds-tabber").children
        next(children)
        for x in children:
           header = x.find('table')
           left_table = x.find('div', class_='lefttablecard')
           right_table = x.find('div', class_='righttablecard')
           potential_eza = unit.find('div', attrs={'style':'float:left; width:100%;'})
           if header == None:
               continue
           header_info = handle_header(header)
           left_info = handle_left(left_table, header_info['unit_id'])
           right_info = handle_right(right_table, potential_eza)
           left_info.update(right_info)
           header_info.update(left_info)
           cards[header_info['unit_id']] = header_info
        for x in cards.keys():
            cards[x]["linked_cards"] = [i for i in cards.keys() if header_info['unit_id'] != i]
        #print(left_info)
        #print(right_info)
        #print(header_info)
        print(cards)
        print('done')
    return cards

"""
Grab all relevant information in the header table of a unit.
Returns a Dictonary
"""
def handle_header(header) -> dict:
    header_info = {'unit_title': None, 'unit_name': None, 'max_lvl': None, 'sa_lvl': None, 'rarity': None, 'unit_type': None,
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
    header_info['sa_lvl'] = third_row_info[1].text.split('/')[1]
    #Grabbing rarity
    if third_row_info[2].find('a'):
        header_info['rarity'] = third_row_info[2].find('a')['href'].split(':')[1]
    else:
        header_info['rarity'] = 'UR'
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
    f_path = './thumbs/'+header_info['unit_id']+'.png'
    if not path.exists(f_path):
        image = header.find('img')
        if 'data-src' in image.attrs:
            img = requests.get(image['data-src'])
        else:
            img = requests.get(image['src'])
        with open(f_path, 'wb') as f:
            f.write(img.content)
        client.upload_file(f_path, bucket_name, 'thumbs/'+header_info['unit_id']+'.png')
    
    return header_info

def handle_left(left_card, uid) -> dict:
    #Grab unit's art
    if not path.exists('./art/'+uid+'.png'):
        image = left_card.find('table').find('img')
        if 'data-src' in image.attrs:
            img = requests.get(image['data-src'])
        else:
            img = requests.get(image['src'])
        f_path = './art/'+uid+'.png'
        with open(f_path, 'wb') as f:
            f.write(img.content)
        client.upload_file(f_path, bucket_name, 'art/'+uid+'.png')
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
    else:
        if len(rows) < 2:
            rows = left_tables[1].find_all('tr')
        cols = rows[1].find_all('td')
        region = cols[0].find('img')['alt'].split()[0].lower()
        if(len(cols) > 2):
            release_date = {region:{'Release':cols[1].text, 'EZA':cols[2].text}}
        else:
            release_date = {region:{'Release':cols[1].text}}
    return release_date
        
def handle_right(right_card, potential_eza) -> dict:
    tables = right_card.find_all('table')
    main_table = tables[0]
    main_rows = []
    unit_attrs = {}
    t = main_table.find('table')
    if t:
        print('yes')
        f = main_table.find_all(class_="wds-tab__content")
        for l in f:
            r = l.find_all('tr')
            for x in r:
               main_rows.append(x)
        stats = tables[4].find_all('center')
        actual_stats = []
        for x in stats:
            if x.text.isdigit():
                actual_stats.append(x.text)
        hp = actual_stats[0:4]
        att = actual_stats[4:8]
        defense = actual_stats[8:12]
        eza_stats = grab_eza_stats(potential_eza)
        for eza in eza_stats:
            unit_attrs[eza] = eza_stats[eza]
    else:
        stats = tables[2].find_all('center')
        actual_stats = []
        for x in stats:
            if x.text.isdigit():
                actual_stats.append(x.text)
        hp = actual_stats[0:4]
        att = actual_stats[4:8]
        defense = actual_stats[8:12]

        print('no')
    t = main_table.find('tbody').find_all('tr')
    for x in t:
        main_rows.append(x)
    unit_sa = 0
    active_condition = None
    for i, row in enumerate(main_rows):
        check = row.find_all('td')
        
        if 'style' in check[0].attrs:
            img = row.find('img')
            if img and 'alt' in img.attrs:
                if 'link' in img['alt'].lower():
                    links = main_rows[i+1].text.strip('\n').split(' - ')
                    temp = []
                    for l in links:
                        temp.append(l.split('Lv')[0][:-1])
                    unit_attrs[img['alt'].split('.png')[0].replace('atk', 'Attack').replace('skill', 'Skill').lower().replace(' ','_')] = temp
                elif 'unit' in img['alt'].lower():
                    index = img['alt'].split('.png')[0].replace('atk', 'Attack').replace('skill', 'Skill')
                    if index not in unit_attrs:
                        unit_attrs[(index + '_' + str(unit_sa)).lower().replace(' ','_')] = re.sub(r'\[\d\]','',main_rows[i+1].text)
                        active_condition = index + ' ' + str(unit_sa) + ' '
                        unit_sa += 1
                    else:
                        unit_attrs[(index + '_' + str(unit_sa)).lower().replace(' ','_')] = re.sub(r'\[\d\]','',main_rows[i+1].text)
                        active_condition = index + ' ' + str(unit_sa) + ' '
                        unit_sa += 1
                elif 'category' in img['alt'].lower():
                    cats = main_rows[i+1].text.strip('\n').split(' - ')
                    temp = []
                    for c in cats:
                        temp.append(c.split('Lv')[0])
                    unit_attrs[img['alt'].split('.png')[0].replace('atk', 'Attack').replace('skill', 'Skill').lower().replace(' ','_')] = temp
                elif len(check) == 2 and ('super' not in img['alt'].lower() and 'passive' not in img['alt'].lower()):
                    unit_attrs[img['alt'].split('.png')[0].replace('atk', 'Attack').replace('skill', 'Skill').lower().replace(' ','_')] = check[1].find('strong').text
                else:
                    if 'activation' in img['alt'].lower() and 'active_skill' in unit_attrs:
                        active_condition = ''
                    index = img['alt'].split('.png')[0].replace('atk', 'Attack').replace('skill', 'Skill')
                    if index in unit_attrs and 'Leader' not in index:
                        unit_attrs[index + ' eza'] = re.sub(r'\[\d\]','',main_rows[i+1].text)
                    else:
                        if index in unit_attrs and 'Activation' in index:
                            unit_attrs[(active_condition + index).lower().replace(' ','_')] = re.sub(r'\[\d\]','',main_rows[i+1].text)
                        elif 'Activation' in index:
                            unit_attrs[(active_condition + index).lower().replace(' ','_')] = re.sub(r'\[\d\]','',main_rows[i+1].text)
                        else:
                            unit_attrs[index.lower().replace(' ','_')] = re.sub(r'\[\d\]','',main_rows[i+1].text)
    unit_attrs['hp'] = hp
    unit_attrs['def'] = defense
    unit_attrs['atk'] = att
    #print(unit_attrs)

    return unit_attrs

def grab_eza_stats(eza_table) -> list:
    stats = eza_table.find_all('center')
    actual_stats = []
    for x in stats:
       if x.text.isdigit():
            actual_stats.append(x.text)
    eza_hp = actual_stats[3:5]
    eza_att = actual_stats[8:10]
    eza_def = actual_stats[13:15]
    return {'EZA_HP' : eza_hp, 'EZA_ATK' : eza_att, 'EZA_DEF' : eza_def}

def setup_unit(url):
    html_response = requests.get(url).text
    soup = BeautifulSoup(html_response, 'lxml')
    all_info = soup.find('div', class_ ='mw-parser-output')
    return all_info

def insert(doc) -> bool:
    try:
        for i in doc:
            unit_collection.insert_one(doc[i])
    except:
        return False
    return True

if __name__ == "__main__":
    all_info = setup_unit('https://dbz-dokkanbattle.fandom.com/wiki/Drive_to_Take_Down_Evil_Pan_(GT)')
    info = grab_unit_info(all_info)
    insert(info)
    #test
    """
    All units have a leader skill, passive, super attack, links, categories
    Some units have an active skill, transformation/exchange/etc., 2 super attacks, unit super attack

    right_info = {leader_skill: string, passive: {passive_name:string}, sa_info: {super_attack_name: string, super_attack_effect: string}, links: [strings], categories: [strings],
                active_skill: {active_skill:string}, change: {type_of_change:string, change_condition: string}, ultsa_info: {super_attack_name: string, super_attack_effect: string}}, 
    """