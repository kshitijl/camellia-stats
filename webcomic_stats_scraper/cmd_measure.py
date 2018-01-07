import json, logging, os

from pythonjsonlogger import jsonlogger

import cmd_shared, timestamp_utils
from page_utils import page_download_directory, timestamped_filename
from snapshot import Snapshot

def initialize_measurement_log(log_filename):
    logger     = logging.getLogger(__name__ + '.measurement_log')
    logHandler = logging.FileHandler(log_filename)
    logHandler.setFormatter(jsonlogger.JsonFormatter())
    logger.addHandler(logHandler)        
    
    logger.setLevel(logging.INFO)
    return logger

def append_to_log(logger, snapshot):
    if not snapshot.measurements:
        logging.info("Nothing to append to log, exiting")
        return
    
    logger.info({'message' : 'Snapshot of measurements',
                 'snapshot': snapshot.to_dict()})

def command(args, config, artifacts):
    measurements_to_extract = cmd_shared.select_artifacts(args.selector,
                                                          artifacts.measurements)
    measure(measurements_to_extract, args.as_of, args.download_dir,
            args.measurements_log)

def measure(measurements_to_extract, as_of, download_dir, measurements_log):    
    measurement_results = {}
    for measurement in measurements_to_extract:
        logging.info({'message': 'Attempting measurement',
                      'as-of'  : timestamp_utils.to_string(as_of),
                      'measurement.name': measurement.name,
                      'page.name': measurement.page.name,
                      'page.url' : measurement.page.url})
        
        page_directory = page_download_directory(download_dir,
                                                 measurement.page.name)
        
        page_filename  = timestamped_filename(page_directory, as_of)

        if not os.path.exists(page_filename):
            logging.error({'message': "Couldn't find downloaded content",
                           'filename': page_filename})
            continue
        
        content = open(page_filename).read()
        try:
            result  = measurement.parse(content)
        
            logging.info({'message': 'Recording measured result',
                          'as-of'  : timestamp_utils.to_string(as_of),
                          'measurement.name': measurement.name,
                          'measurement-result': result})
            
            measurement_results[measurement.name] = result
        except BaseException as e:
            logging.info({'message': 'Measurement failed',
                          'exception': e})
    
    append_to_log(initialize_measurement_log(measurements_log),
                  Snapshot(as_of, measurement_results))
