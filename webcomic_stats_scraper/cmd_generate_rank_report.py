import report_generation

def command(args, config, artifacts):
    rank_observables = [o for o in artifacts.observables if o.is_rank_observable]
    observations     = report_generation.observations_from_log(rank_observables,
                                                               args.measurement_log)
    
                                                                        
