#!/usr/bin/env python

import elasticsearch as ES

from load_testdb import INDEX
from translator.translator import translate, Hits, Equal

es = ES.Elasticsearch()

body = translate(
    Hits(7),
    [],
    [Equal('title', 'Test2')])

from pprint import pprint
origin_data = es.search(index=INDEX, body=body)
pprint(origin_data)

print
print 'format:'
from translator.post_process import _format, hits_sources
pprint(hits_sources(_format(origin_data)))
