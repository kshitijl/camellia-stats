def command(args, config_object, artifacts):
    pages_to_download = select_artifacts(args.selector, artifacts.pages)

    import datetime
    timestamp = datetime.datetime.now()

    logging.info({'message'  : 'starting downloads',
                  'timestamp': format_timestamp(timestamp),
                  'config'   : config_object})

    from page_utils import page_download_directory, save_content_to_timestamped_file_in_dir
    for page in pages_to_download:
        content = page.download()

        download_directory = page_download_directory(config_object.download_dir, page.name)
        logging.info({"message": "Writing downloaded content to timestamped file",
                      "download_dir": download_directory})
        save_content_to_timestamped_file_in_dir(content, download_directory, timestamp)
