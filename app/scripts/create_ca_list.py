import os
import csv

ca_units = []

with open('data/CCAS_Affiliations.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:

        base_item = {}
        count = 0
        aor = []
        for r in row:
            if count == 0:
                base_item['Program'] = r
                count +=1
            elif count == 1:
                base_item['Unit'] = r
                ca_units.append((r, r))
                count += 1
            elif count > 1 and r != '':
                aor.append(r)
                count += 1
        base_item['AOR'] = aor
        
print(ca_units)