#!/usr/bin/env python

import argparse

import cmd_download, cmd_measure, config, timestamp, initialize_logging
from desired_artifacts import all_artifacts
        
def main():
    parser = argparse.ArgumentParser(
        description="Tools for downloading and scraping webcomic stats") 

    parser.add_argument('--config-file', type=file, default='./config.json')
    parser.add_argument('--selector'   , type=str , default=None)
    subparsers = parser.add_subparsers(help='Subcommands implementing steps in the pipeline')

    parser_download              = subparsers.add_parser('download-pages',
                                                         help='Download some or all pages')
    parser_measure               = subparsers.add_parser('measure',
                                                         help='Extract numbers or other data from downloaded html content')
    parser_generate_report       = subparsers.add_parser('generate-report'      , help='Process the raw extracted data to generate a CSV report')
    parser_download_and_measure  = subparsers.add_parser('download-and-measure',
                                                         help='Run [download] followed by [measure] on the downloaded content')


    parser_measure.add_argument('--as-of', type=timestamp.parse, required=True)

    parser_download            .set_defaults(func=cmd_download.command)
    parser_measure             .set_defaults(func=cmd_measure.command)
    # parser_generate_report     .set_defaults(func=cmd_generate_report)
    # parser_download_and_measure.set_defaults(func=cmd_download_and_measure)
    
    args = parser.parse_args()

    initialize_logging.log_in_json_format()        

    config_object = config.load_config(args.config_file)

    artifacts = all_artifacts(config_object)

    args.func(args, config_object, artifacts)

if __name__ == "__main__":
    main()
