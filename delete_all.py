#!/usr/bin/env python

from load_testdb import INDEX, DOC_TYPE

import elasticsearch as ES

# connect to localhost:9200
es = ES.Elasticsearch()

# delete all
print es.delete_by_query(index=INDEX, body={'query_string': {'query': '*'}})
print es.indices.delete_mapping(index=INDEX, doc_type=DOC_TYPE)
