#


class Table(dict):

    def __init__(self, data=None):

        def construct(v):
            if isinstance(v, dict):
                return Table(v)
            elif isinstance(v, (list, tuple, set)):
                return type(v)(map(lambda e: construct(e), v))
            else:
                return v

        if isinstance(data, dict):
            for k, v in data.iteritems():
                self[k] = construct(v)
        else:
            raise TypeError(
                'Expect data to be a dict but found %s' % type(data))

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError('Attribute "%s" not found' % name)

    def __setattr__(self, name, value):
        self[name] = value


class Slots(object):
    def __init__(self):
        self.container = {}

    def put(self, key, value):
        try:
            self.container[key].append(value)
        except KeyError:
            self.container[key] = []

    def get(self, key):
        try:
            return self.container[key]
        except KeyError:
            return []

    def __iter__(self):
        return iter(self.container)
