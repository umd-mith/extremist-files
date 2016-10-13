#!/usr/bin/env python3

"""

This program crawls the Extremist Files section of the SPLC website
and extracts some basic information about people and organizations 
that are there. After it has run you should see two sets of files:

    * individuals.json
    * individuals.csv
    * groups.json
    * groups.csv

The CSV files are normalized for a collaborative editing exercise and do not
have all the information that is present in the JSON files.

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
    resp = http.get(url, headers={"User-Agent": "extremist-files-urls: https://github.com/edsu/extremist-files-urls"})
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

def map_name():
    features = requests.get('https://www.splcenter.org/hate-map.geojson').json()['features']
    seen = set([g['name'].lower() for g in json.load(open('groups.json'))])



def write_csv():
    fieldnames = ['Name', 'Researcher', 'Verified By', 'Twitter', 'Facebook', 'YouTube', 'SPLC', 'Notes']
   
    w = csv.DictWriter(open('extremist-files.csv', 'w'), fieldnames=fieldnames)
    w.writeheader()
    for group in json.load(open('groups.json')):
        w.writerow({
            "Name": group['name'],
            "SPLC": group['url']
        })
    for person in json.load(open('individuals.json')):
        w.writerow({
            "Name": person['name'],
            "SPLC": person['url']
        })

if __name__ == "__main__":
    logging.basicConfig(filename="crawl.log", level=logging.INFO)
    json.dump(list(groups()), open('groups.json', 'w'), indent=2)
    json.dump(list(individuals()), open('individuals.json', 'w'), indent=2)
    write_csv()
