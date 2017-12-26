#!/usr/bin/env python

import os, datetime, hashlib
from lxml import html

from common import *

class Config:
    content_cache_dir = './downloaded-stats-pages'

def shasum(text):
    return hashlib.sha256(text).hexdigest()

def exact_tree_from_xpath(content, selector):
    return html.fromstring(content).xpath(selector)[0]

class Page(object):
    def __init__(self, url, statistics):
        self.url, self.statistics = url, statistics

    def cache_directory(self):
        return os.path.join(Config.content_cache_dir, shasum(self.url))

    def lookup_content_in_cache(self, as_of):
        filename = timestamped_filename(self.cache_directory(), as_of)
        try:
            return file(filename).read()
        except:
            raise KeyError("No data available for {}".format(as_of))
        
    def download_and_save_content(self):
        content = download_with_user_agent(self.url)
        save_content_to_dated_file_in_dir(content, self.cache_directory())
        
    def retrieve_content(self, as_of):
        if not self.lookup_content_in_cache(as_of):
            self.download_and_save_content()
        return self.lookup_content_in_cache(as_of)

    def all_statistics(self):
        return self.statistics.keys()

    def __getitem__(self, key):
        return self.statistics[key]

class Webtoons_statistic(object):
    def __init__(self, xpath):
        self.xpath = xpath

    def parse(self, content):
        scraped_text = exact_tree_from_xpath(content, self.xpath)
        return parse_number_with_commas(scraped_text)

class Scraped_statistics(object):
    def __init__(self, stats_dict):
        self.stats_dict = stats_dict

    def all_stats(self):
        answer = []
        
        for page_name, page in self.stats_dict.iteritems():
            for statistic in page.all_statistics():
                answer.append(page_name + "." + statistic)

        return answer

    def lookup_statistic(self, statistic_name):
        page, stat = statistic_name.split(".")
        return self.stats_dict[page], self.stats_dict[page][stat]

    def scrape_one(self, statistic_name, as_of):
        page, statistic = self.lookup_statistic(statistic_name)
        content         = page.retrieve_content(as_of)

        return statistic.parse(content)

    def scrape_all(self, as_of):
        return { stat: self.scrape_one(stat, as_of) for stat in self.all_stats() }
    
def main():    
    stats = Scraped_statistics({
        'webtoons': Page(
            url='http://www.webtoons.com/challenge/titleStat?titleNo=81223',
            statistics={
                'subs': Webtoons_statistic(
                    xpath='//*[@id="content"]/div[2]/div[2]/div/div[2]/ul[1]/li[3]/span/text()'),
                'montly_pvs': Webtoons_statistic(
                    xpath='//*[@id="content"]/div[2]/div[2]/div/div[2]/ul[2]/li[3]/span/text()'),
                'likes': Webtoons_statistic(
                    xpath='//*[@id="content"]/div[2]/ul/li/div/p[2]/em/text()')})})

    print stats.scrape_all(as_of=datetime.datetime(2017, 12, 26, 00, 32))

if __name__ == "__main__":
    main()
