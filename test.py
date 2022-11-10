import parse_disam
import get_disams

import parse_unit

links = []

y = 0

for x in get_disams.get_disams():
    test = parse_disam.parse_disambiguation(x)
    print(test)
    links.append(test)
    y += 1
    if y == 6:
        break

for array in links:
    for link in array:
        print(link)
        all_info = parse_unit.setup_unit(link)
        info = parse_unit.grab_unit_info(all_info)
        parse_unit.insert(info)