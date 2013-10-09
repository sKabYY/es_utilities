import json

from datetime import datetime


def dumps(data):
    def the_default(data):
        if isinstance(data, datetime):
            return data.isoformat()

    return json.dumps(data, default=the_default)


def loads(s):
    return json.load(s)
