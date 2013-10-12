class table(dict):

    def __init__(self, data=None, key_mapper=None):
        if isinstance(data, dict):
            self.update(data)
        elif isinstance(data, (list, tuple, set)):
            if key_mapper is None:
                key_mapper = lambda x: x
            for e in data:
                self[key_mapper(e)] = e

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError('Attribute "%s" not found' % name)

    def __setattr__(self, name, value):
        self[name] = value
