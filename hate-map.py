#!/usr/bin/env python

"""
Save unique names from SPLC Hate Map geo-json as CSV.
"""

import csv
import json
import requests

map_data = requests.get('https://www.splcenter.org/hate-map.geojson', headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"}).json() 

# there are lots of addresses for the same organization
# we are interested in just the unique names so we can
# look for their social media and web urls

names = set()
for feature in map_data['features']:
    names.add(feature['properties']['name'])

names = list(names)
names.sort()

out = csv.writer(open("hate-map.csv", "w"))
out.writerow(['Name', 'Twitter', 'Facebook', 'Website'])

for name in names:
    out.writerow([name, None, None, None])
