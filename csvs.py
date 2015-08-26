#!/usr/bin/env python

import csv
import json

cols = ['name', 'url', 'born', 'died', 'group']
writer = csv.writer(open('individuals.csv', 'wb'))
writer.writerow(cols + ['twitter', 'facebook', 'website'])
for i in json.load(open('individuals.json')):
    row = [i[col].encode('utf8') for col in cols] + [None, None, None]
    writer.writerow(row)

cols = ['name', 'url', 'location', 'ideology']
writer = csv.writer(open('groups.csv', 'wb'))
writer.writerow(cols + ['twitter', 'facebook', 'website'])
for i in json.load(open('groups.json')):
    row = [i[col].encode('utf8') for col in cols] + [None, None, None]
    writer.writerow(row)




