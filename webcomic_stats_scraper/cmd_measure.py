import json, logging, os

import cmd_shared, timestamp_utils
from page_utils import page_download_directory, timestamped_filename

def append_to_log(log_filename, as_of, contents):
    if not contents:
        logging.info("Nothing to append to log, exiting")
        return
    
    timestamp = timestamp_utils.to_string(as_of)
    what_to_write = {'timestamp': timestamp}
    what_to_write.update(contents)

    logging.info("Appending successful scrapes to event-log: %s",
                 str(what_to_write))

    with open(log_filename, 'a') as output_file:
        json.dump(what_to_write, output_file)
        output_file.write('\n')

def command(args, config, artifacts):
    measurements_to_extract = cmd_shared.select_artifacts(args.selector,
                                                          artifacts.measurements)
    
    measurement_results = {}
    for measurement in measurements_to_extract:
        logging.info({'message': 'Attempting measurement',
                      'as-of'  : timestamp_utils.to_string(args.as_of),
                      'measurement.name': measurement.name,
                      'page.name': measurement.page.name,
                      'page.url' : measurement.page.url})
        
        page_directory = page_download_directory(config.download_dir,
                                                 measurement.page.name)
        
        page_filename  = timestamped_filename(page_directory, args.as_of)

        if not os.path.exists(page_filename):
            logging.error({'message': "Couldn't find downloaded content",
                           'filename': page_filename})
            continue
        
        content = file(page_filename).read()
        result  = measurement.parse(content)

        logging.info({'message': 'Recording measured result',
                      'as-of'  : timestamp_utils.to_string(args.as_of),
                      'measurement.name': measurement.name,
                      'measurement-result': result})
        
        measurement_results[measurement.name] = result
    
    append_to_log(config.measurements_log,
                  args.as_of,
                  measurement_results)
