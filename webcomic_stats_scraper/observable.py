class Observable(object):
    def __init__(self, measurement, transformation):
        self.measurement, self.transformation = measurement, transformation

def identity(m):
    return Observable(m, lambda x: x)
