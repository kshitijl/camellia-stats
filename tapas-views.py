#!/usr/bin/env python

import requests
from lxml import html

def download_with_user_agent(url):
    # We need to send a User-Agent or else Tapas returns a 403
    # Forbidden.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; \
        Intel Mac OS X 10_11_5) AppleWebKit/537.36 \
        (KHTML, lik} Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    return requests.get(url,headers=headers).content

def download_comic_home_page(comic_name):
    return download_with_user_agent('http://tapas.io/series/{}'.format(comic_name))

def extract_pageviews_string_from_html(content):
    parsed_tree = html.fromstring(content)
    
    xpath_query_for_pageviews_li = '//ul[@class="number-status"]/li[@class="common-tooltip"]'
    xpath_query_result = parsed_tree.xpath(xpath_query_for_pageviews_li)

    def make_error_message(s):
        return "Looks like Tapas changed their HTML layout;\
        couldn't find pageviews in the usual place. In particular, {}".format(s)
    
    if xpath_query_result == []:
        raise AttributeError(make_error_message("The usual li in a ul wasn't present"))

    li_tag_containing_pageviews = xpath_query_result[0]
    if "data-title" not in li_tag_containing_pageviews.attrib:
        raise AttributeError(make_error_message("The 'data-title' attribute wasn't in the li"))

    return li_tag_containing_pageviews.attrib["data-title"]

def parse_number_with_commas(s):
    return int(s.replace(',', ''))

def parse_pageviews_string(pageviews_string):
    if not pageviews_string.endswith(' views'):
        raise AttributeError("Expected a string that ends with the ' views', got: {}".format(pageviews_string))
    numeric_string = pageviews_string[:-len(' views')]
    return parse_number_with_commas(numeric_string)

def save_content_to_dated_file_in_dir(content, directory, as_of=None):
    import datetime
        
    if not as_of:
        as_of = datetime.datetime.now()
        
    time_string = datetime.datetime.strftime(as_of, "%Y-%m-%d-%H-%M")

    import os
    filename = os.path.join(directory, time_string)

    with open(filename, 'w') as output_file:
        output_file.write(content)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Download and parse pageviews for Camellia on Tapas")
    parser.add_argument('--download-location',
                        type=str,
                        default='./downloaded-stats-pages/tapas-camellia-home-page',
                        help="The downloaded html will be saved to file named the current time in this directory")
    parser.add_argument('--input-file-instead-of-downloading', type=str, default=None)

    args = parser.parse_args()
    
    if args.input_file_instead_of_downloading:
        comic_homepage_html = file(args.input_file_instead_of_downloading).read()
    else:
        comic_homepage_html = download_comic_home_page('Camellia')
        save_content_to_dated_file_in_dir(comic_homepage_html, args.download_location)
        
    print parse_pageviews_string(extract_pageviews_string_from_html(comic_homepage_html))

if __name__ == "__main__":
    main()
