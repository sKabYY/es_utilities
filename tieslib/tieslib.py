import elasticsearch as ES

from translator.translator import (
    translate,
    Equal, Range, Prefix,
    And, Or, Not,
    Hits, Terms, Histogram
)
from translator.post_process import (
    _format,
    hits_sources, facet_terms, facet_entries,
)
from interp.tilib import (
    le2nd, eq2nd, inrange,
    setup_environment,
)
from interp.titype import mkvoid, mkprimitive


__global_url = 'localhost'
__global_port = '9200'
__global_index = '*'
__global_doc_type = '*'


def connect(url, port):
    global __global_url
    global __global_port
    __global_url = url
    __global_port = port
    return mkvoid()


def set_index(index):
    global __global_index
    __global_index = index
    return mkvoid()


def get_index():
    return __global_index


def set_doc_type(doc_type):
    global __global_doc_type
    __global_doc_type = doc_type
    return mkvoid()


def get_doc_type():
    return __global_doc_type


def prompt():
    return '%s:%s/%s/%s' % (
        __global_url, __global_port,
        __global_index, __global_doc_type,
    )


def es_search(post_data):
    es = ES.Elasticsearch([{
        'host': __global_url,
        'post': __global_port,
    }])
    return _format(es.search(
        index=__global_index,
        doc_type=__global_doc_type,
        body=post_data
    ))


def add_default(args, default_list):
    '''
    '''
    res = list(args)
    start = len(res)
    end = len(default_list)
    while start < end:
        res.append(default_list[start])
        start += 1
    return res


# functions ################################################


def translate_hits(*args):
    '''
    args: [size, fields, conditions, sort]
    '''
    size, fields, conditions, sort = add_default(args, [10, [], [], None])
    h = Hits(size, fields,  None, sort)
    if not isinstance(conditions, list):
        conditions = [conditions]
    post_data = translate(h, [], conditions)
    return post_data


def search_hits(*args):
    post_data = translate_hits(*args)
    return hits_sources(es_search(post_data))


__global_terms_tags = '__terms__'


def translate_terms(*args):
    '''
    args: [field, size, conditions]
    '''
    field, size, conditions = add_default(args, [None, 10, []])
    t = Terms(__global_terms_tags, field, size)
    post_data = translate(Hits(0), [t], conditions)
    return post_data


def search_terms(*args):
    post_data = translate_terms(*args)
    return facet_terms(__global_terms_tags, es_search(post_data))


__global_histogram_tags = '__histogram__'


def translate_histogram(*args):
    '''
    args: [timestamp_field, interval, conditions]
    '''
    ts_field, interval, conditions = add_default(args, [None, 'hour', []])
    h = Histogram(__global_histogram_tags, ts_field, interval)
    post_data = translate(Hits(0), [h], conditions)
    return post_data


def search_histogram(*args):
    post_data = translate_histogram(*args)
    return facet_entries(__global_histogram_tags, es_search(post_data))


###########################################################


def ties_primitive_procedures():
    PM = [
        # environment
        ('connect', connect, eq2nd(2)),
        ('set-index!', set_index, eq2nd(1)),
        ('get-index', get_index, eq2nd(0)),
        ('set-doc-type!', set_doc_type, eq2nd(1)),
        ('get-doc-type', get_doc_type, eq2nd(0)),
        # conditions
        ('Equal', Equal, eq2nd(2)),
        ('Range', Range, eq2nd(3)),
        ('Prefix', Prefix, eq2nd(2)),
        ('And', lambda *conds: And(conds), le2nd(1)),
        ('Or', lambda *conds: Or(conds), le2nd(1)),
        ('Not', Not, eq2nd(1)),
        # translate and search
        ('translate-hits', translate_hits, le2nd(4)),
        ('search-hits', search_hits, le2nd(4)),
        ('translate-terms', translate_terms, inrange(1, 4)),
        ('search-terms', search_terms, inrange(1, 4)),
        ('translate-histogram', translate_histogram, inrange(1, 3)),
        ('search-histogram', search_histogram, inrange(1, 3)),
    ]
    return map(lambda (s, b, a): (s, mkprimitive(s, a, b)), PM)


def setup_ties_environment():
    env = setup_environment()
    env.putall(ties_primitive_procedures())
    return env
