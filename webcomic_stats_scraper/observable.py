class Observable(object):
    def __init__(self, name, measurement, transformation):
        self.name, self.measurement = name, measurement
        self.transformation         = transformation

def identity(m):
    return Observable(m.name, m, lambda x: x)

def rank_of_comic_in(comic_name, creator_name, comics_measurement):
    def matches(s1, s2):
        return (s1.lower() in s2.lower()) or (s2.lower() in s1.lower())
    
    def get_rank(comics):
        for idx, (featured_comic, featured_creator, _) in enumerate(comics):
            if matches(comic_name, featured_comic) \
               and matches(creator_name, featured_creator):
                return idx+1
        return None

    observable_name = "rank-in." + comics_measurement.name
    return Observable(observable_name, comics_measurement, get_rank)
