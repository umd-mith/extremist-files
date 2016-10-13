#!/usr/bin/env python

import csv
import json
import requests

features = requests.get('https://www.splcenter.org/hate-map.geojson').json()['features']

fieldnames = ['Name', 'Researcher', 'Verified By', 'Twitter', 'Facebook',
        'YouTube', 'SPLC', 'Notes']
w = csv.DictWriter(open('map.csv', 'w'), fieldnames=fieldnames)
w.writeheader()

# only add them if we haven't already seen them
seen = set([g['name'].lower() for g in json.load(open('groups.json'))])

for feature in features:
    name = feature['properties']['name']
    if name.lower() in seen:
        continue
    w.writerow({'Name': name})
    seen.add(name.lower())
