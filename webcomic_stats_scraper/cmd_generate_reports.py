from report_generation import flatten_by_timestamp, observations_from_log
from report_generation import with_empty_cells_set_to_none, all_measurement_names
from report_generation import write_csv, sort_by_timestamp

from snapshot import Snapshot

def generate_daily_report(all_observables, measurement_log, output_filename):
    def date_of_timestamp(timestamp):
        return timestamp.date()
    
    def select_last_snapshot_from_each_day(snapshots):
        last_snapshot_for_date = {}

        for snapshot in sort_by_timestamp(snapshots):
            last_snapshot_for_date[date_of_timestamp(snapshot.timestamp)] = snapshot
            
        return last_snapshot_for_date.values()
    
    generate_report_with_selected_rows(all_observables, measurement_log,
                                       output_filename,
                                       select_last_snapshot_from_each_day)

def generate_rank_report(all_observables, measurement_log, output_filename):
    rank_observables = [o for o in all_observables if o.is_rank_observable]
    generate_report_with_selected_rows(rank_observables, measurement_log,
                                       output_filename,
                                       lambda observations: observations)

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

def with_difference_from_previous_row(spreadsheet):
    return flatten_by_timestamp(spreadsheet + differences_of(spreadsheet))

def generate_full_report(all_observables, measurement_log, output_filename):
    generate_report_with_selected_rows(all_observables, measurement_log, output_filename,
                                       lambda observations: observations)
    
def generate_report_with_selected_rows(all_observables, measurement_log, output_filename,
                                       selector_function):
    observations    = observations_from_log(all_observables, measurement_log)

    selected_observations = selector_function(observations)

    write_observation_snapshots_and_their_diffs_to_csv(selected_observations,
                                                       output_filename)

def write_observation_snapshots_and_their_diffs_to_csv(observations, output_filename):   
    spreadsheet  = sort_by_timestamp(with_empty_cells_set_to_none(observations))
    with_diffs   = with_difference_from_previous_row(spreadsheet)

    write_snapshots_to_csv(with_diffs, output_filename)

def write_snapshots_to_csv(snapshots, output_filename):
    final_report = with_empty_cells_set_to_none(snapshots)
    write_csv(sort_by_timestamp(final_report), file(output_filename, 'w'))

def command(args, config, artifacts):
    generate_rank_report (artifacts.observables, args.measurements_log, args.rank_report)
    generate_daily_report(artifacts.observables, args.measurements_log, args.daily_report)
    generate_full_report (artifacts.observables, args.measurements_log, args.full_report)
