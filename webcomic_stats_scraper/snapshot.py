import timestamp_utils

class Snapshot(object):
    def __init__(self, timestamp, measurements):
        assert measurements is not None
        self.timestamp, self.measurements = timestamp, measurements
        
    @staticmethod
    def from_data_dict(data_dict):
        timestamp = timestamp_utils.of_string(data_dict['timestamp'])
        measurements = data_dict['measurements']

        return Snapshot(timestamp, measurements)

    def to_dict(self):
        return {'timestamp'   : timestamp_utils.to_string(self.timestamp),
                'measurements': self.measurements}

    def map_measurements(self, f):
        return Snapshot(self.timestamp, f(self.measurements))

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return str(self)
