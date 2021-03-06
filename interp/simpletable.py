class SimpleTable(dict):

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


def enum(*seq, **params):
    try:
        key_mapper = params['key_mapper']
    except KeyError:
        key_mapper = lambda x: x
    return SimpleTable(seq, key_mapper)


def mktable(**kwargs):
    return SimpleTable(kwargs)
