#!/usr/bin/env python

import os, datetime, hashlib
from lxml import html

from common import *

class Config:
    content_cache_dir = './downloaded-stats-pages'
    log_filename      = './scrape-events-log'

def sha256_hexencoded(text):
    return hashlib.sha256(text).hexdigest()

def exact_tree_from_xpath(content, selector):
    return html.fromstring(content).xpath(selector)[0]

class Page(object):
    def __init__(self, retriever, statistics):
        self.retriever, self.statistics = retriever, statistics

    def cache_directory(self):
        return os.path.join(Config.content_cache_dir, self.retriever.shasum())

    def lookup_content_in_cache(self, as_of):
        filename = timestamped_filename(self.cache_directory(), as_of)
        try:
            return file(filename).read()
        except:
            return None
        
    def download_and_save_content(self):
        content = self.retriever.retrieve()
        save_content_to_dated_file_in_dir(content, self.cache_directory())
        return content
        
    def retrieve_content(self, as_of):
        if as_of is None:
            maybe_answer = self.lookup_content_in_cache(datetime.datetime.now())
            if maybe_answer:
                return maybe_answer
            else:
                return self.download_and_save_content()
        else:
            answer = self.lookup_content_in_cache(as_of)
            if not answer:
                raise KeyError("Requested content for {} is not in cache".format(as_of))
            return answer

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

    def scrape_one(self, statistic_name, as_of=None):
        page, statistic = self.lookup_statistic(statistic_name)
        content         = page.retrieve_content(as_of)

        return statistic.parse(content)

    def scrape_all(self, as_of=None):
        return { stat: self.scrape_one(stat, as_of) for stat in self.all_stats() }

def append_to_log(log_filename, as_of, contents):
    timestamp = datetime.datetime.strftime(as_of, "%Y-%m-%d-%H-%M")
    what_to_write = {timestamp: contents}
    print "Writing", what_to_write

    import json
    with open(log_filename, 'a') as output_file:
        json.dump(what_to_write, output_file)
        output_file.write('\n')

class Webtoons_logged_in_retriever(object):
    webtoons_login_url = 'http://m.webtoons.com/member/login/doLoginById'
    
    def __init__(self, url, username, password):
        self.url, self.username, self.password = url, username, password

    def retrieve(self):
        from splinter import Browser

        with Browser('chrome') as browser:
            browser.visit(self.webtoons_login_url)

            username_field = browser.find_by_id("emailId")[0]
            username_field.fill(self.username)

            password_field = browser.find_by_id("password")[0]
            password_field.fill(self.password)

            import time
            
            login_button = browser.find_by_id("btnLogIn")[0]
            time.sleep(5)
            login_button.click()
            time.sleep(5)

            browser.visit(self.url)
            desired_content = browser.html

        return desired_content

    def shasum(self):
        return sha256_hexencoded(self.url + self.username)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Download and parse statistics")
    parser.add_argument('--username', type=str, required=True)
    parser.add_argument('--password', type=str, required=True)

    args = parser.parse_args()

    stats = Scraped_statistics({
        'webtoons': Page(
            retriever=Webtoons_logged_in_retriever(
                url='http://www.webtoons.com/challenge/titleStat?titleNo=81223',
                username=args.username,
                password=args.password),
            statistics={
                'subs': Webtoons_statistic(
                    xpath='//*[@id="content"]/div[2]/div[2]/div/div[2]/ul[1]/li[3]/span/text()'),
                'montly_pvs': Webtoons_statistic(
                    xpath='//*[@id="content"]/div[2]/div[2]/div/div[2]/ul[2]/li[3]/span/text()'),
                'likes': Webtoons_statistic(
                    xpath='//*[@id="content"]/div[2]/ul/li/div/p[2]/em/text()')})})

    append_to_log(Config.log_filename,
                  datetime.datetime.now(),
                  stats.scrape_all())

if __name__ == "__main__":
    main()
