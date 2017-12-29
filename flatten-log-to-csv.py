#!/usr/bin/env python

import sys, json, collections

def flatten_results_per_timestamp(events):
    flattened = collections.defaultdict(dict)
    
    for event in events:
        for date, measurements in event.iteritems():
            for measurement_name,measurement_result in measurements.iteritems():
                flattened[date][measurement_name] = measurement_result

    return flattened

def flatten_and_postprocess(events):
    flattened = flatten_results_per_timestamp(events)
    measurement_names = all_measurement_names(flattened)

    # TODO for now, just undersample: grab the measurement closest to
    # 9pm every day.

    # timestamp -> {observable_name: value}
    basic_observables = observables_of_measurements(flattened)

    # timestamp -> {observable_name_diff: value} (but not for first timestamp)
    difference_from_previous_observables = differences_of(measurement_names,
                                                          basic_observables)

    all_observables = merge_observations(basic_observables,
                                         difference_from_previous_observables)

    return all_observables

def to_csv(observations):
    import csv
    
    observable_names = all_measurement_names(observations)

    rows = fill_out_empty_cells(observations,
                                column_names=observable_names)
    print rows    

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Download and parse statistics")
    parser.add_argument('--input-log-file', type=str, default=sys.stdin)
    parser.add_argument('--output-file',    type=str, default=sys.stdout)

    args = parser.parse_args()
    
    events = [json.loads(line) for line in args.input_log_file.readlines()]

    json.dump(flatten_and_postprocess(events), args.output_file)

if __name__ == "__main__":
    main()
