#!/usr/bin/env python
#
# !WARNING: This script may rewrite the data in your local elasticsearch!
#

INDEX = 'testdb'
DOC_TYPE = 'testtest'
DOC_TYPE2 = 'testdiff'

if __name__ == '__main__':
    from datetime import timedelta

    import common.timeutils as tt
    import elasticsearch as ES

    def testtest(es):
        ts_field = 'datetime'
        head = ('title', 'content', 'num')
        num_cols = len(head)
        data = [
            ('Test', 'Hehe', 1),
            ('T2', 'Lala', 2),
            ('Tst2', 'Xaxa', 3),
            ('Tes2', 'Kaka', 4),
            ('Test9', 'Kala', 5),
            ('Test2', 'Lala', 6),
            ('Test2', 'Lala', 7),
            ('Test12', 'Lala', 8),
            ('Test22', 'Lala', 8),
            ('Test32', 'Lala', 7),
        ]

        now = tt.get_now()

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

            es.create(
                index=INDEX,
                doc_type=DOC_TYPE,
                id=i + 1,
                body=body
            )

    def testdiff(es):
        T = 3
        N = 10
        for i in xrange(T):
            for j in xrange(N):
                idx = i + 1
                body = {
                    'name': '#%d' % idx,
                    'total': j * idx,
                    'timestamp': tt.get_now()
                }
                es.create(
                    index=INDEX,
                    doc_type=DOC_TYPE2,
                    id=i * N + j + 1,
                    body=body
                )

    # connect to localhost:9200
    es = ES.Elasticsearch()

    es.indices.create(index=INDEX)

    testtest(es)
    testdiff(es)
    print 'ok'
