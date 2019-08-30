import os
import csv
from elasticsearch import Elasticsearch

es = Elasticsearch('http://localhost:9200')

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
                count += 1
            elif count > 1 and r != '':
                aor.append(r)
                count += 1
        base_item['AOR'] = aor
        
        result = es.index(index='ca_units',doc_type='unit', body=base_item)
        print(result)