import json, collections, csv

import timestamp_utils
from snapshot import Snapshot

def all_measurement_names(snapshot_log):
    return set.union(*[set(snapshot.measurements.keys()) for snapshot in snapshot_log])

def merge_dicts(*args):
    answer = dict()
    for dd in args:
        answer.update(dd)

    return answer

def with_empty_cells_set_to_none(snapshots):
    all_nones = {measurement_name : None for measurement_name in all_measurement_names(snapshots)}

    def overlay_available_measurements(measurements):
        return merge_dicts(all_nones, measurements)
    
    return [snapshot.map_measurements(overlay_available_measurements) \
            for snapshot in snapshots]

def flatten_by_timestamp(snapshots_log):
    by_timestamp = collections.defaultdict(dict)
     
    for snapshot in snapshots_log:
        timestamp    = snapshot.timestamp
        measurements = snapshot.measurements
        
        for measurement_name, measurement_result in measurements.iteritems():
            by_timestamp[timestamp][measurement_name] = measurement_result

    timestamps_in_order = sorted(by_timestamp.keys())
    return [Snapshot(timestamp, by_timestamp[timestamp]) for timestamp in timestamps_in_order]

def compute_observations(observables, snapshots):
    def compute_all_observables(measurements):
        answer = {}
        for observable in observables:
            if observable.measurement.name not in measurements:
                continue
            
            measured_input = measurements[observable.measurement.name]
            answer[observable.name] = observable.transformation(measured_input)
        return answer
        
    return [snapshot.map_measurements(compute_all_observables) for snapshot in snapshots]

def write_csv(snapshots, output_file):
    writer = csv.writer(output_file, delimiter=',')

    column_names = sorted(all_measurement_names(snapshots))
    writer.writerow(['timestamp'] + column_names)

    for row in snapshots:
        values = row.measurements
        timestamp_str = timestamp_utils.to_string(row.timestamp)
        line = [timestamp_str] + [values[name] for name in column_names]
        writer.writerow(line)
