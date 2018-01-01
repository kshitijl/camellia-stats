#!/usr/bin/env python

import argparse

import cmd_download, cmd_measure, cmd_generate_report
import config, timestamp_utils, initialize_logging

from desired_artifacts import all_artifacts

def add_download_dir_argument(parser):
    parser.add_argument('--download-dir', type=str,
                        default="./output-artifacts/downloaded-pages")
    
def add_measurements_log_argument(parser):
    parser.add_argument('--measurements-log', type=str,
                        default="./output-artifacts/measurements-log")
        
def main():
    parser = argparse.ArgumentParser(
        description="Tools for downloading and scraping webcomic stats") 

    parser.add_argument('--config-file', type=file, default='./config.json')
    parser.add_argument('--selector'   , type=str , default=None)
    subparsers = parser.add_subparsers(help='Subcommands implementing steps in the pipeline')

    parser_download = subparsers.add_parser('download-pages',
        help='Download some or all pages')
    add_download_dir_argument(parser_download)
    
    parser_measure = subparsers.add_parser('measure', \
        help='Extract numbers or other data from downloaded html content')
    parser_measure.add_argument('--as-of', type=timestamp_utils.of_string, required=True)    
    add_download_dir_argument(parser_measure)
    add_measurements_log_argument(parser_measure)    
    
    parser_generate_report = subparsers.add_parser('generate-report',
        help='Process the raw extracted data to generate a CSV report')
    add_measurements_log_argument(parser_generate_report)
    parser_generate_report.add_argument('--generated-report',
                                        type=str,
                                        default="./output-artifacts/current-report.csv")
    
    parser_download_and_measure  = subparsers.add_parser('download-and-measure',
        help='Run [download] followed by [measure] on the downloaded content')

    parser_download            .set_defaults(func=cmd_download.command)
    parser_measure             .set_defaults(func=cmd_measure.command)
    parser_generate_report     .set_defaults(func=cmd_generate_report.command)
    # parser_download_and_measure.set_defaults(func=cmd_download_and_measure)
    
    args = parser.parse_args()

    initialize_logging.log_in_json_format()        

    config_object = config.load_config(args.config_file)
    artifacts = all_artifacts(config_object)
    args.func(args, config_object, artifacts)

if __name__ == "__main__":
    main()
