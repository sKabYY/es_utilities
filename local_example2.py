#!/usr/bin/env python
# test diff

from pprint import pprint
import elasticsearch as ES
from translator.translator import translate, Hits
from translator.post_process import _format, hits_sources
from translator.post_process import groupby, difference


post_data = translate(
    Hits(50, ['name', 'total'], sort={'timestamp': 'asc'}),
    [], [])

es = ES.Elasticsearch()
from load_testdb import INDEX, DOC_TYPE2

origin_data = es.search(index=INDEX, doc_type=DOC_TYPE2, body=post_data)

formatted_data = _format(origin_data)
sources = hits_sources(formatted_data)
print 'sources:'
pprint(sources)

print

diff = map(lambda l: difference(l, 'total'), groupby(sources, 'name'))
print 'diff'
pprint(diff)
