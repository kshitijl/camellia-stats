#!/usr/bin/env python

import os, datetime, hashlib, logging, traceback
logging.basicConfig(level=logging.INFO)

from lxml import html
import requests

class Config:
    content_cache_dir = './downloaded-stats-pages'
    log_filename      = './scrape-events-log'
    comic_name        = 'Camellia'
    creator_name      = 'ladypcpx'

def download_with_user_agent(url):
    # We need to send a User-Agent or else Tapas returns a 403
    # Forbidden.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; \
        Intel Mac OS X 10_11_5) AppleWebKit/537.36 \
        (KHTML, lik} Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    # n.b. [.text] returns the decoded [.content]
    return requests.get(url,headers=headers).text

def parse_number_with_commas(s):
    return int(s.replace(',', ''))

def format_timestamp(as_of):
    return datetime.datetime.strftime(as_of, "%Y-%m-%d-%H-%M")

def timestamped_filename(directory, as_of):
    time_string = format_timestamp(as_of)
    return os.path.join(directory, time_string)

def save_content_to_timestamped_file_in_dir(content, directory, as_of):
    if os.path.exists(directory):
        if not os.path.isdir(directory):
            raise AttributeError("{} exists but is not a directory".format(directory))
    else:
        os.makedirs(directory)
        
    filename = timestamped_filename(directory, as_of)
    with open(filename, 'w') as output_file:
        output_file.write(content.encode('utf-8'))

def chop_suffix(text, suffix, error_message=None):
    if not text.endswith(suffix):
        raise AttributeError("Expected a string that ends with '{}', got: {}".
                             format(suffix, text))
    return text[:-len(suffix)]

def sha256_hexencoded(text):
    return hashlib.sha256(text).hexdigest()

def exact_tree_from_xpath(content, selector):
    return html.fromstring(content).xpath(selector)[0]

class Cached_as_of(object):
    can_be_considered_current = False
    def __init__(self, time):
        self.time = time

    def __str__(self):
        return "Cached_as_of {}".format(format_timestamp(self.time))        

class Current_as_of(object):
    can_be_considered_current = True    
    def __init__(self, time):
        self.time = time

    def __str__(self):
        return "Current_as_of {}".format(format_timestamp(self.time))

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
        
    def download_and_save_content(self, current_time):
        logging.info("Downloading %s as-of %s",
                     self.retriever.url,
                     format_timestamp(current_time))
        content = self.retriever.retrieve()
        
        logging.info("Caching %s as-of %s",
                     self.retriever.url,
                     format_timestamp(current_time))
        save_content_to_timestamped_file_in_dir(content, self.cache_directory(), current_time)
        return content
        
    def retrieve_content(self, as_of):
        if as_of.can_be_considered_current:
            maybe_answer = self.lookup_content_in_cache(as_of.time)
            if maybe_answer:
                return maybe_answer
            else:
                return self.download_and_save_content(as_of.time)
        else:
            answer = self.lookup_content_in_cache(as_of.time)
            if not answer:
                raise KeyError("Requested content for {} is not in cache".format(as_of.time))
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

def number_in_thousands_with_suffix_K(text):
    return int(float(chop_suffix(text, suffix='K')) * 1000)

def body_of_tag(content, xpath):
    return exact_tree_from_xpath(content, xpath)

class Number_in_thousands_with_suffix_K_body_of_tag(object):
    def __init__(self, xpath):
        self.xpath = xpath

    def parse(self, content):
        return number_in_thousands_with_suffix_K(
            body_of_tag(content, self.xpath))

def float_between_0_and_10(text):
    answer = float(text)
    if not 0 < answer < 10:
        raise ValueError("Expected a number between 0 and 10, got {}".format(text))
    return answer        
    
class Float_between_0_and_10_body_of_tag(object):
    def __init__(self, xpath):
        self.xpath = xpath

    def parse(self, content):
        return float_between_0_and_10(
            body_of_tag(content, self.xpath))

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

        logging.info("Retrieving %s as-of %s", statistic_name, str(as_of))
        content         = page.retrieve_content(as_of)

        logging.info("Parsing %s", statistic_name)
        return statistic.parse(content)

    def scrape_all(self, as_of):
        return self.scrape_some(self.all_stats(), as_of)

    def scrape_some(self, stats, as_of):
        answer = {}
        for stat in stats:
            try:
                answer[stat] = self.scrape_one(stat, as_of)
            except BaseException as e:
                logging.info("There was trouble scraping %s", stat)
                logging.info(traceback.format_exc())
        return answer

def append_to_log(log_filename, as_of, contents):
    if not contents:
        logging.info("Nothing to append to log, exiting")
        return
    
    timestamp = format_timestamp(as_of)
    what_to_write = {timestamp: contents}

    logging.info("Appending successful scrapes to event-log: %s",
                 str(what_to_write))

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

        with Browser('chrome', headless=True) as browser:
            browser.visit(self.webtoons_login_url)

            username_field = browser.find_by_id("emailId")[0]
            username_field.fill(self.username)

            password_field = browser.find_by_id("password")[0]
            password_field.fill(self.password)

            import time
            time.sleep(5)
            
            login_button = browser.find_by_id("btnLogIn")[0]
            login_button.click()

            browser.visit(self.url)
            desired_content = browser.html

        return desired_content

    def shasum(self):
        return sha256_hexencoded(self.url + self.username)

class Plain_url_retriever(object):
    def __init__(self, url):
        self.url = url

    def retrieve(self):
        return download_with_user_agent(self.url)

    def shasum(self):
        return sha256_hexencoded(self.url)

class Tapas_views(object):
    def extract_pageviews_string_from_html(self, content):
        xpath_selector = '//ul[@class="number-status"]/li[@class="common-tooltip"]'
        li_tag_containing_pageviews = exact_tree_from_xpath(content, xpath_selector)

        if "data-title" not in li_tag_containing_pageviews.attrib:
            raise AttributeError(make_error_message("The 'data-title' attribute wasn't in the li"))
        
        return li_tag_containing_pageviews.attrib["data-title"]

    def parse(self, content):
        pageviews_string = self.extract_pageviews_string_from_html(content)
        
        return parse_number_with_commas(chop_suffix(pageviews_string, suffix=' views'))

class Tapas_subs(object):
    def __init__(self, creator_name):
        self.creator_name = creator_name

    def extract_subscribers_string_from_html(self, content):
        xpath_selector = '//a[@href="/{}/subscribers"]/text()'.format(self.creator_name)
        xpath_query_result = html.fromstring(content).xpath(xpath_selector)

        return ''.join([x for x in ''.join(xpath_query_result).strip() if x not in ' \n'])

    def parse(self, content):
        subs_string = self.extract_subscribers_string_from_html(content)

        return parse_number_with_commas(chop_suffix(subs_string, suffix='Subscribers'))

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Download and parse statistics")
    parser.add_argument('statistics', type=str, nargs='*')
    parser.add_argument('--webtoons-username', type=str, required=True)
    parser.add_argument('--webtoons-password', type=str, required=True)

    def timestamp(t):
        return Cached_as_of(datetime.datetime.strptime(t, '%Y-%m-%d-%H-%M'))
    
    parser.add_argument('--as-of'   , type=timestamp,
                        default=Current_as_of(datetime.datetime.now()))

    args = parser.parse_args()

    stats = Scraped_statistics({
        'tapas-comic-page': Page(
            retriever=Plain_url_retriever('http://tapas.io/series/{}'.format(Config.comic_name)),
            statistics={ 'views': Tapas_views() }),
        
        'tapas-creator-page': Page(
            retriever=Plain_url_retriever('https://tapas.io/{}/subscribers'.format(Config.creator_name)),
            statistics={ 'subs': Tapas_subs(Config.creator_name) }),

        'webtoons-public-comic-page': Page(
            retriever=Plain_url_retriever('http://www.webtoons.com/en/challenge/camellia/list?title_no=81223'.format(Config.creator_name)),
            statistics={
                'views': Number_in_thousands_with_suffix_K_body_of_tag(                
                    xpath='//*[@id="_asideDetail"]/ul/li[2]/em/text()'),
                'rating': Float_between_0_and_10_body_of_tag(                
                    xpath='//*[@id="_starScoreAverage"]/text()')                
            },
        ),
                
        'webtoons': Page(
            retriever=Webtoons_logged_in_retriever(
                url='http://www.webtoons.com/challenge/titleStat?titleNo=81223',
                username=args.webtoons_username,
                password=args.webtoons_password),
            statistics={
                'subs': Webtoons_statistic(
                    xpath='//*[@id="content"]/div[2]/div[2]/div/div[2]/ul[1]/li[3]/span/text()'),
                'montly_pvs': Webtoons_statistic(
                    xpath='//*[@id="content"]/div[2]/div[2]/div/div[2]/ul[2]/li[3]/span/text()'),
                'likes': Webtoons_statistic(
                    xpath='//*[@id="content"]/div[2]/ul/li/div/p[2]/em/text()')})})

    if not args.statistics:
        scrape_result = stats.scrape_all(as_of=args.as_of)
    else:
        scrape_result = stats.scrape_some(args.statistics, as_of=args.as_of)

    append_to_log(Config.log_filename,
                  args.as_of.time,
                  scrape_result)

if __name__ == "__main__":
    main()
