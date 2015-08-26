#!/usr/bin/env python

import re
import json
import time
import requests

from urlparse import urljoin
from bs4 import BeautifulSoup

def get(url):
    time.sleep(1) # be nice
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"})
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
        doc = get(url)
        name = doc.find('h1').text
        location = first(doc, '.field-name-field-extremist-location .field-item')
        ideology = first(doc, '.field-name-field-ideology a')
        desc = first(doc, '.field-name-field-long-text p')
        yield {
            "url": url,
            "name": name,
            "ideology": ideology,
            "location": location,
            "description": desc,
        }

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
        doc = get(url)
        name = doc.find('h1').text
        born = first(doc, '.field-name-field-extremist-dates span')
        died = first(doc, '.field-name-field-extremist-dates-end span')
        desc = first(doc, '.field-name-field-long-text p')
        ideology = first(doc, '.field-name-field-ideology a')
        group = first(doc, '.field-name-field-group a')
        yield {
            "url": url,
            "name": name,
            "born": born,
            "died": died,
            "ideology": ideology,
            "group": group,
            "description": desc
        }

json.dump(list(groups()), open('groups.json', 'w'), indent=2)
json.dump(list(individuals()), open('individuals.json', 'w'), indent=2)
