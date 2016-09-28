import json
import os
import feedparser

from config import *


class RSS(object):
    @classmethod
    def store_sites_rss(cls):
        for site_name, site_xml in NEWS_SITES.iteritems():
            cls.store_site_rss(site_name, site_xml)

    @staticmethod
    def store_site_rss(site_name, site_xml):
        file_name = os.path.join(os.path.dirname(__file__), 'data', site_name) + ".json"
        if os.path.isfile(file_name):
            with open(file_name, 'r') as f:
                data = json.loads(f.read())
        else:
            data = {}
        rss = feedparser.parse(site_xml)
        entries = rss['entries']
        for entry in entries:
            data[entry['link']] = entry['title']
        with open(file_name, 'w') as f:
            f.write(json.dumps(data, indent=4))

RSS.store_sites_rss()