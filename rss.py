import json
import os
import feedparser
import time

from config import *


class RSS(object):
    @classmethod
    def sources(cls):
        with open(RSS.sources_file()) as f:
            return json.loads(f.read())

    @classmethod
    def sources_file(cls):
        return os.path.join(os.path.dirname(__file__), 'sources.json')

    @classmethod
    def store_sites_rss(cls, progress_callback=None):
        sources = cls.sources()
        total = len(sources)
        current = 0
        for site_name, site_xml in sources.iteritems():
            if progress_callback:
                if not progress_callback(current, total, site_name):
                    return
            current += 1
            cls.store_site_rss(site_name, site_xml)

    @classmethod
    def store_site_rss(cls, site_name, site_xml):
        file_name = site_name + ".json"
        data = cls.load_file_data(file_name)
        rss = feedparser.parse(site_xml)
        entries = rss['entries']
        for entry in entries:
            data[entry['link']] = entry['title']
        cls.save_file_data(file_name, data)

    @classmethod
    def load_file_data(cls, file_name):
        file_path = os.path.join(cls.data_path(), file_name)
        if not os.path.isfile(file_path):
            return {}
        with open(file_path) as f:
            return json.loads(f.read())

    @classmethod
    def save_file_data(cls, file_name, data):
        file_path = os.path.join(cls.data_path(), file_name)
        with open(file_path, 'w') as f:
            f.write(json.dumps(data, indent=4))

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
    def load_all_news_as_array(cls):
        result = []
        for file_name in RSS.stored_files():
            data = RSS.load_file_data(file_name)
            for link, title in data.iteritems():
                result.append({"link": link, "title": title})
        return result

    @classmethod
    def stored_files(cls):
        return os.listdir(cls.data_path())

    @classmethod
    def data_path(cls):
        return os.path.join(os.path.dirname(__file__), 'data')

if __name__ == '__main__':
    print "Before", json.dumps(RSS.count_stored_rss(), indent=4)
    print "Working...",
    start_time = time.time()
    RSS.store_sites_rss()
    print "Finished after ", time.time() - start_time, "ms"
    print "After", json.dumps(RSS.count_stored_rss(), indent=4)
