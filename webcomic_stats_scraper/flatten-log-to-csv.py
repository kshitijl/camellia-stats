#!/usr/bin/env python

import sys, json, collections

from common import *

def merge_dicts(*args):
    answer = dict()

    for dd in args:
        answer.update(dd)

    return answer

class Snapshot(object):
    def __init__(self, timestamp, measurements):
        assert measurements is not None
        self.timestamp, self.measurements = timestamp, measurements
        
    @staticmethod
    def from_data_dict(data_dict):
        timestamp = parse_timestamp(data_dict['timestamp'])
        measurements = {k:v for (k,v) in data_dict.iteritems() if k != 'timestamp'}

        return Snapshot(timestamp, measurements)

    def to_data_dict(self):
        return merge_dicts({'timestamp': format_timestamp(self.timestamp)}, self.measurements)

    def map_measurements(self, f):
        return Snapshot(self.timestamp, f(self.measurements))

    def __str__(self):
        return str(self.to_data_dict())

    def __repr__(self):
        return str(self)    
    
def flatten_by_timestamp(snapshots_log):
    by_timestamp = collections.defaultdict(dict)
     
    for snapshot in snapshots_log:
        timestamp = snapshot.timestamp
        measurements = snapshot.measurements
        
        for measurement_name,measurement_result in measurements.iteritems():
            by_timestamp[timestamp][measurement_name] = measurement_result

    return [Snapshot(timestamp, by_timestamp[timestamp]) for timestamp in sorted(by_timestamp.keys())]

def all_measurement_names(snapshot_log):
    return set.union(*[set(snapshot.measurements.keys()) for snapshot in snapshot_log])

def set_empty_cells_to_none(snapshots):
    all_nones = {measurement_name : None for measurement_name in all_measurement_names(snapshots)}
    
    return [Snapshot(snapshot.timestamp, merge_dicts(all_nones, snapshot.measurements)) for snapshot in snapshots]

def differences_of(snapshots, measurements_to_diff):
    answer = []

    def diff_measurement_name(measurement_name):
        return measurement_name + '.diff'

    for row_before, row_after in zip(snapshots, snapshots[1:]):
        diff = {}
        for measurement in measurements_to_diff:
            before = row_before.measurements[measurement]
            after  = row_after.measurements[measurement]
            
            if (after is not None) and (before is not None):
                diff_measurement = after - before
            else:
                diff_measurement = None
                
            diff[diff_measurement_name(measurement)] = diff_measurement
            
        answer.append(Snapshot(row_after.timestamp, diff))

    return answer

def flatten_and_postprocess(snapshot_log):
    snapshot_set = flatten_by_timestamp(snapshot_log)

    # TODO feature: for now, just undersample: grab the measurement
    # closest to 9pm every day.

    basic_observables = set_empty_cells_to_none(observables_of_measurements(snapshot_set))

    # TODO cleanliness: This is business logic, declare it with the observable.
    def is_rank_statistic(name):
        return name.startswith('tapas') and name.endswith('comics-in-order')
    
    to_diff = [name for name in all_measurement_names(snapshot_log) if not is_rank_statistic(name)]
    
    difference_from_previous_observables = differences_of(basic_observables, to_diff)

    all_observables = flatten_by_timestamp(basic_observables + difference_from_previous_observables)
    
    return set_empty_cells_to_none(all_observables)

def to_csv(snapshots, output_file):
    import csv

    writer = csv.writer(output_file, delimiter=',')

    column_names = ['timestamp'] + sorted(all_measurement_names(snapshots))
    writer.writerow(column_names)

    for row in snapshots:
        data_dict = row.to_data_dict()
        line = [data_dict[name] for name in column_names]
        writer.writerow(line)

def observables_of_measurements(snapshots):
    # TODO cleanliness: This is business logic. It should be declared
    # and passed into the generic plumbing above. 
    def compute_observables(measurements):
        answer = {}
        
        for name, value in measurements.iteritems():
            # default pass-through
            observable_name = name
            observed_value  = value
            
            if name.startswith('tapas') and name.endswith('comics-in-order'):
                observable_name = name.split('.')[0] + '.rank'
                observed_value  = 'Not on front page'
                
                for idx, (comic_name, creator, _) in enumerate(value):
                    if comic_name.lower() == 'camellia' and 'ladypcpx' in creator:
                        observed_value = idx
                        break

            answer[observable_name] = observed_value
        return answer
    
    return [snapshot.map_measurements(compute_observables) for snapshot in snapshots]
    
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Download and parse statistics")
    parser.add_argument('--input-log-file', type=file, default=sys.stdin)
    parser.add_argument('--output-file',    type=file, default=sys.stdout)

    args = parser.parse_args()
    
    events = [Snapshot.from_data_dict(json.loads(line)) for line in args.input_log_file.readlines()]
    snapshot_log = sorted(events, key=lambda x: x.timestamp)
    to_csv(flatten_and_postprocess(snapshot_log), args.output_file)

if __name__ == "__main__":
    main()
