import cmd_download, cmd_measure

def command(args, config_object, artifacts):
    all_pages = artifacts.pages
    timestamp_of_download = cmd_download.download(all_pages, args.download_dir)

    all_measurements = artifacts.measurements
    cmd_measure.measure(all_measurements, timestamp_of_download,
                        args.download_dir, args.measurement_log)
