import json, collections, csv

import timestamp_utils, report_columns
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
        
        for measurement_name, measurement_result in measurements.items():
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

    available_columns = all_measurement_names(snapshots)
    column_names = [x for x in report_columns.columns_in_order if report_columns.our_name_for(x) in available_columns]
    writer.writerow(['timestamp'] + column_names)

    for row in snapshots:
        values = row.measurements
        timestamp_str = timestamp_utils.to_string(row.timestamp)
        line = [timestamp_str] + [values[report_columns.our_name_for(name)] for name in column_names]
        writer.writerow(line)

def sort_by_timestamp(snapshots):
    return list(sorted(snapshots, key=lambda snapshot:snapshot.timestamp))

def observations_from_log(observables, log_filename):
    snapshots = [Snapshot.from_data_dict(json.loads(line)['snapshot']) \
                 for line in open(log_filename).readlines()]

    snapshot_log = sorted(snapshots, key=lambda snapshot:snapshot.timestamp)
    observations = compute_observations(observables, flatten_by_timestamp(snapshot_log))

    return observations
    
