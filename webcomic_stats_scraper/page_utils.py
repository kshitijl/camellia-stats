import os, hashlib

import timestamp_utils

def page_download_directory(download_dir, page_name):
    return os.path.join(download_dir, page_name)

def timestamped_filename(directory, as_of):
    time_string = timestamp_utils.to_string(as_of)
    return os.path.join(directory, time_string)

def save_content_to_timestamped_file_in_dir(content, directory, timestamp):
    if os.path.exists(directory):
        if not os.path.isdir(directory):
            raise AttributeError("{} exists but is not a directory".format(directory))
    else:
        os.makedirs(directory)

    filename = timestamped_filename(directory, timestamp)
    with open(filename, 'wb') as output_file:
        output_file.write(content.encode('utf-8'))

def sha256_hexencoded(text):
    return hashlib.sha256(text).hexdigest()
