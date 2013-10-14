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

pprint(es.search(index=INDEX, body=body))
