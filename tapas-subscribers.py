#!/usr/bin/env python

from lxml import html
import common

def download_creator_subscriber_page(creator_name):
    return common.download_with_user_agent('https://tapas.io/{}/subscribers'.format(creator_name))

def extract_subscribers_string_from_html(content, creator_name):
    parsed_tree = html.fromstring(content)

    xpath_query_for_subs = '//a[@href="/ladypcpx/subscribers"]/text()'
    xpath_query_result = parsed_tree.xpath(xpath_query_for_subs)

    def make_error_message(s):
        return "Looks like Tapas changed their HTML layout;\
        couldn't find subs in the usual place. In particular, {}".format(s)
    
    if xpath_query_result == []:
        raise AttributeError(make_error_message("The usual link to /$creator/subscribers wasn't present"))

    return ''.join([x for x in ''.join(xpath_query_result).strip() if x not in ' \n'])

def parse_subscribers_string(subs_string):
    if not subs_string.endswith('Subscribers'):
        raise AttributeError("Expected a string that ends with the 'Subscribers', got: {}".format(subs_string))

    numeric_string = subs_string[:-len('Subscribers')]
    return common.parse_number_with_commas(numeric_string)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Download and parse subs for ladypcpx on Tapas")
    parser.add_argument('--download-location',
                        type=str,
                        default='./downloaded-stats-pages/tapas-ladypcpx-subscribers-page',
                        help="The downloaded html will be saved to file named the current time in this directory")
    parser.add_argument('--input-file-instead-of-downloading', type=str, default=None)

    args = parser.parse_args()
    creator_name = 'ladypcpx'
    
    if args.input_file_instead_of_downloading:
        html_content = file(args.input_file_instead_of_downloading).read()
    else:
        html_content = download_creator_subscriber_page(creator_name)
        common.save_content_to_dated_file_in_dir(html_content, args.download_location)
        
    print parse_subscribers_string(extract_subscribers_string_from_html(html_content, creator_name))

if __name__ == "__main__":
    main()
    
