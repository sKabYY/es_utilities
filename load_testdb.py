#!/usr/bin/env python
#
# !WARNING: This script may rewrite the data in your local elasticsearch!
#

from datetime import timedelta

import common.timeutils as tt
import elasticsearch as ES

INDEX = 'testdb'
DOC_TYPE = 'testtest'


def main():
    ts_field = 'datetime'
    head = ('title', 'content')
    num_cols = len(head)
    data = [
        ('Test', 'Hehe'),
        ('T2', 'Lala'),
        ('Tst2', 'Xaxa'),
        ('Tes2', 'Kaka'),
        ('Test9', 'Kala'),
        ('Test2', 'Lala'),
        ('Test2', 'Lala'),
        ('Test12', 'Lala'),
        ('Test22', 'Lala'),
        ('Test32', 'Lala'),
    ]

    now = tt.get_now()

    # connect to localhost:9200
    es = ES.Elasticsearch()

    # put template
    #es.indices.put_template(name='testdb', body={
    #    'template': INDEX,
    #    'settings': {
    #        'index.analysis.analyzer.default.type': 'simple'},
    #    'mappings': {
    #        '_all': {'enabled': False},
    #        '_source': {'compress': True},
    #        DOC_TYPE: {
    #            'dynamic_templates': [{
    #                'title_template': {
    #                    'path_match': 'title',
    #                    'match_mapping_type': 'string',
    #                    'mapping': {
    #                        'type': 'string',
    #                        'index': 'not_analyzed'}}}]}}})

    # put mapping
    es.indices.put_mapping(index=INDEX, doc_type=DOC_TYPE, body={
        'testdb_testtest_mapping': {
            'properties': {
                'title': {'type': 'string', 'index': 'not_analyzed'}
            }
        }
    })

    for i in xrange(len(data)):

        body = {ts_field: now + timedelta(hours=1)}
        for j in xrange(num_cols):
            body[head[j]] = data[i][j]

        es.index(
            index=INDEX,
            doc_type=DOC_TYPE,
            id=i + 1,
            body=body
        )

    from pprint import pprint
    # show all
    pprint(es.search())

if __name__ == '__main__':
    main()
