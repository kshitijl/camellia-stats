import datetime

def of_string(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d-%H-%M')

def to_string(t):
    return datetime.datetime.strftime(t, "%Y-%m-%d-%H-%M")
