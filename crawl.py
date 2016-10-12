#!/usr/bin/env python3

"""

This program crawls the Extremist Files section of the SPLC website
and extracts some basic information about people and organizations 
that are there. It also uses the geojson of their map to pull in 
additional organizations that may not be present on the SPLC list.

After it has run you should see two sets of files:

    * individuals.json
    * individuals.csv
    * groups.json
    * groups.csv

The CSV files are normalized for a collaborative editing exercise and do not
have all the information present in the JSON files.

"""

import re
import csv
import json
import time
import logging
import requests

from urllib.parse import urljoin
from bs4 import BeautifulSoup

http = requests.Session()

def get(url):
    time.sleep(1) # be nice
    resp = http.get(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"})
    return BeautifulSoup(resp.content, 'html.parser')

def first(element, selector):
    results = element.select(selector)
    if len(results) > 0:
        text = results[0].text
        text = text.replace("\n", " ")
        text = re.sub("  +", " ", text)
        return text.strip()
    return ""

def group_urls():
    url = 'https://www.splcenter.org/fighting-hate/extremist-files/groups'
    doc = get(url)
    urls = set()
    for a in doc.select('.field-item a'):
        if '/fighting-hate/extremist-files/group/' in a['href']:
            urls.add(urljoin(url, a['href']))
    return urls

def groups():
    for url in group_urls():
        logging.info("getting group %s", url)
        doc = get(url)
        name = doc.find('h1').text
        location = first(doc, '.field-name-field-extremist-location .field-item')
        ideology = first(doc, '.field-name-field-ideology a')
        desc = first(doc, '.field-name-field-long-text p')
        result = {
            "url": url,
            "name": name,
            "ideology": ideology,
            "location": location,
            "description": desc,
        }
        logging.info("found: %s", json.dumps(result))
        yield result

def individual_urls():
    url = 'https://www.splcenter.org/fighting-hate/extremist-files/individual'
    doc = get(url)
    urls = set()
    for a in doc.select('.field-item a'):
        if '/fighting-hate/extremist-files/individual/' in a['href']:
            urls.add(urljoin(url, a['href']))
    return urls


def individuals():
    for url in individual_urls():
        logging.info("getting individual %s", url)
        doc = get(url)
        name = doc.find('h1').text
        born = first(doc, '.field-name-field-extremist-dates span')
        died = first(doc, '.field-name-field-extremist-dates-end span')
        desc = first(doc, '.field-name-field-long-text p')
        ideology = first(doc, '.field-name-field-ideology a')
        group = first(doc, '.field-name-field-group a')
        result = {
            "url": url,
            "name": name,
            "born": born,
            "died": died,
            "ideology": ideology,
            "group": group,
            "description": desc
        }
        logging.info("found %s", json.dumps(result))
        yield result

def norm(name):
    return name.lower().strip()

def write_csvs():
    seen = set()
    fieldnames = ['Name', 'Researcher', 'Verified By', 'SPLC', 'Twitter', 'Facebook', 'YouTube', 'Notes']
   
    iw = csv.DictWriter(open('individuals.csv', 'w'), fieldnames=fieldnames)
    iw.writeheader()
    for person in json.load(open('individuals.json')):
        name = person['name']
        name_norm = norm(name)
        seen.add(name_norm)
        iw.writerow({
            "Name": name,
            "SPLC": person['url']
        })

    gw = csv.DictWriter(open('groups.csv', 'w'), fieldnames=fieldnames)
    gw.writeheader()
    for group in json.load(open('groups.json')):
        name = group['name']
        url = group['url']
        name_norm = norm(name)
        if name_norm in seen:
            continue
        seen.add(name_norm)
        gw.writerow({
            "Name": name,
            "SPLC": url
        })
 
    # TODO: move this into a separate function? 
    map_data = requests.get('https://www.splcenter.org/hate-map.geojson', headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"}).json() 
    for feature in map_data['features']:
        props = feature['properties']
        name = props['name']
        name_norm = norm(name)
        if name_norm in seen:
            continue
        seen.add(name_norm)
        url = None
        if props['group']:
            m = re.search('href="(.+)">', props['group'])
            if m:
                url = m.group(1)
                if url in seen:
                    logging.info("already seen %s with %s", name, url)
                    continue
                seen.add(url)
                logging.info("map has %s with url %s", name, url)
                gw.writerow({
                    "Name": name,
                    "SPLC": url
                })


if __name__ == "__main__":
    logging.basicConfig(filename="crawl.log", level=logging.INFO)
    #json.dump(list(groups()), open('groups.json', 'w'), indent=2)
    #json.dump(list(individuals()), open('individuals.json', 'w'), indent=2)
    write_csvs()
