import logging, datetime

import cmd_shared, timestamp_utils
from page_utils import page_download_directory, save_content_to_timestamped_file_in_dir

def command(args, config_object, artifacts):
    pages_to_download = cmd_shared.select_artifacts(args.selector, artifacts.pages)

    timestamp = datetime.datetime.now()

    logging.info({'message'  : 'starting downloads',
                  'timestamp': timestamp_utils.to_string(timestamp),
                  'config'   : config_object})

    for page in pages_to_download:
        content = page.download()

        download_directory = page_download_directory(args.download_dir, page.name)
        logging.info({"message": "Writing downloaded content to timestamped file",
                      "download_dir": download_directory})
        save_content_to_timestamped_file_in_dir(content, download_directory, timestamp)
