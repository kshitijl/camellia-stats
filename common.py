import os, datetime

import requests


def download_with_user_agent(url):
    # We need to send a User-Agent or else Tapas returns a 403
    # Forbidden.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; \
        Intel Mac OS X 10_11_5) AppleWebKit/537.36 \
        (KHTML, lik} Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    return requests.get(url,headers=headers).content

def parse_number_with_commas(s):
    return int(s.replace(',', ''))

def timestamped_filename(directory, as_of):
    time_string = datetime.datetime.strftime(as_of, "%Y-%m-%d-%H-%M")
    return os.path.join(directory, time_string)

def save_content_to_dated_file_in_dir(content, directory, as_of=None):
    import datetime
        
    if not as_of:
        as_of = datetime.datetime.now()

    filename = timestamped_filename(directory, as_of)
    with open(filename, 'w') as output_file:
        output_file.write(content)

def chop_suffix(text, suffix, error_message=None):
    if not pageviews_string.endswith(suffix):
        raise AttributeError("Expected a string that ends with '{}', got: {}".
                             format(suffix, text))
    return text[:-len(suffix)]
    
