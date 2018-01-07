import json

class Config(object):
    def __str__(self):
        visible_config = {k:v for (k,v) in self.__dict__.items() if 'password' not in k}
        return str(visible_config)

def load_config(config_file):
    answer = Config()
    
    answer.__dict__.update(json.load(config_file))

    return answer
