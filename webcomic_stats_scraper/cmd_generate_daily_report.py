import report_generation

def differences_of(snapshots):
    def diff_measurement_name(measurement_name):
        return measurement_name + '.diff'

    measurements_to_diff = all_measurement_names(snapshots)    
    
    answer = []
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

def with_difference_from_previous(spreadsheet):
    return flatten_by_timestamp(spreadsheet + differences_of(spreadsheet))

def command(args, config, artifacts):
    all_observables = artifacts.observables

    snapshots = [Snapshot.from_data_dict(json.loads(line)['snapshot']) \
                 for line in file(args.measurements_log).readlines()]

    snapshot_log = sorted(snapshots, key=lambda snapshot:snapshot.timestamp)
    observations = compute_observations(observables, flatten_by_timestamp(snapshot_log))
    spreadsheet  = with_empty_cells_set_to_none(observations)
    with_diffs   = with_difference_from_previous(spreadsheet)
    final_report = with_empty_cells_set_to_none(with_diffs)

    write_csv(final_report, file(args.daily_report, 'w'))
