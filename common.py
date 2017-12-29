import datetime

def parse_timestamp(t):
    return datetime.datetime.strptime(t, '%Y-%m-%d-%H-%M')

def format_timestamp(as_of):
    return datetime.datetime.strftime(as_of, "%Y-%m-%d-%H-%M")
