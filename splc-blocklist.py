#!/usr/bin/env python

import os
import re
import csv
import codecs
import logging
import twitter
import urllib.request

logging.basicConfig(filename="splc-blocklist.log", level=logging.WARN)

e = os.environ
tw = twitter.Api(
    consumer_key=e['CONSUMER_KEY'],
    consumer_secret=e['CONSUMER_SECRET'],
    access_token_key=e['ACCESS_TOKEN_KEY'],
    access_token_secret=e['ACCESS_TOKEN_SECRET']
)

# the night against hate spreadsheet
csv_url = 'https://docs.google.com/a/umd.edu/spreadsheets/d/1LsJHAdSexX4yoYq_Pgfb7XWZgRmBuCcS-7QEETfHxlA/export?format=csv'

http_stream = urllib.request.urlopen(csv_url)
csv_reader = csv.DictReader(codecs.iterdecode(http_stream, 'utf-8'))
csv_writer = open("splc-blocklist.csv", "w")

first = True
for row in csv_reader:

    twitter_url = row['Twitter'].strip()
    if not twitter_url or twitter_url == "?":
        continue

    m = re.match('^https://twitter.com/([a-zA-Z0-9_]+)$', twitter_url)
    if not m:
        logging.warn("found unexpected twitter handle: %s", twitter_url)
        continue

    screen_name = m.group(1)

    user = tw.GetUser(screen_name=screen_name)
    if user:
        # so weird that Twitter's blocklist importer expects
        # there to not be a end of line at the end of the file
        # it's true, try it yourself if you don't believe me!
        if first:
            first = False
        else:
            csv_writer.write("\n")
        csv_writer.write(str(user.id))
    else:
        logging.warn("unknown twitter user: %s",  screen_name)
