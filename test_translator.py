#!/usr/bin/env python

from datetime import timedelta

import common.timeutils as tt

from translator.translator import translate
from translator.translator import Hits, Range, Histogram, Equal, Terms
from pprint import pprint

count = 1


def test(hits, facets, conditions):
    global count
    print '#%s' % count
    data = translate(hits, facets, conditions)
    pprint(data)
    import connection.esjson as J
    print J.dumps(data)
    count += 1
    return data

# some predefined global variable
now = tt.get_now()
start = now - timedelta(days=1)
end = now
ts_field = '@timestamp'
timerange = Range(ts_field, start, end)

#
test(Hits(0), [], [])

#
test(
    Hits(10, ['toDomain', 'hehe']),
    [],
    [
        timerange
    ])

#
test(
    Hits(0),
    [Histogram('traffic', ts_field, 'hour')],
    [
        timerange,
        Equal('status', 'Deferred')
    ])

#
test(
    Hits(0),
    [Terms('To domain', 'toDomain', 7)],
    [
        timerange
    ])

#
test(
    Hits(0),
    [Histogram('traffic', ts_field, 'hour', Equal('status', 'Deferred')),
     Terms('To domain', 'toDomain', 7)],
    [
        timerange
    ])
