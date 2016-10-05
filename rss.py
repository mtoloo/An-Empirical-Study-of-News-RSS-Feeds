import json
import os
import feedparser

from config import *


class RSS(object):
    @classmethod
    def store_sites_rss(cls):
        for site_name, site_xml in NEWS_SITES.iteritems():
            cls.store_site_rss(site_name, site_xml)

    @classmethod
    def store_site_rss(cls, site_name, site_xml):
        file_name = site_name + ".json"
        if os.path.isfile(file_name):
            data = cls.load_file_data(file_name)
        else:
            data = {}
        rss = feedparser.parse(site_xml)
        entries = rss['entries']
        for entry in entries:
            data[entry['link']] = entry['title']
        with open(file_name, 'w') as f:
            f.write(json.dumps(data, indent=4))

    @classmethod
    def load_file_data(cls, file_name):
        with open(os.path.join(cls.data_path(), file_name)) as f:
            return json.loads(f.read())

    @classmethod
    def count_file_rss(cls, file_name):
        with open(os.path.join(cls.data_path(), file_name)) as f:
            return len(json.loads(f.read()))

    @classmethod
    def count_stored_rss(cls):
        result = {file_name: cls.count_file_rss(file_name) for file_name in cls.stored_files()}
        result['Total'] = sum(result.values())
        return result

    @classmethod
    def stored_files(cls):
        return os.listdir(cls.data_path())

    @classmethod
    def data_path(cls):
        return os.path.join(os.path.dirname(__file__), 'data')

if __name__ == '__main__':
    print "Before", json.dumps(RSS.count_stored_rss(), indent=4)
    RSS.store_sites_rss()
    print "After", json.dumps(RSS.count_stored_rss(), indent=4)
