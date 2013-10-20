import elasticsearch as ES

from translator.translator import (
    translate,
    Equal, Range,
    And, Or, Not,
    Hits,
)
from translator.post_process import (
    _format, hits_sources,
)
from interp.tilib import (
    le2nd, eq2nd,
    setup_environment,
)
from interp.titype import mkvoid, mkprimitive


__global_url = 'localhost'
__global_port = '9200'
__global_index = '*'


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


def prompt():
    return '%s:%s/%s' % (__global_url, __global_port, __global_index)


def es_search(post_data):
    es = ES.Elasticsearch([{
        'host': __global_url,
        'post': __global_port,
    }])
    return _format(es.search(index=__global_index, body=post_data))


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


def ties_primitive_procedures():
    PM = [
        # environment
        ('connect', connect, eq2nd(2)),
        ('set-index!', set_index, eq2nd(1)),
        ('get-index', get_index, eq2nd(0)),
        # conditions
        ('Equal', Equal, eq2nd(2)),
        ('Range', Range, eq2nd(3)),
        ('And', lambda *conds: And(conds), le2nd(1)),
        ('Or', lambda *conds: Or(conds), le2nd(1)),
        ('Not', Not, eq2nd(1)),
        # translate and search
        ('translate-hits', translate_hits, le2nd(4)),
        ('search-hits', search_hits, le2nd(4)),
    ]
    return map(lambda (s, b, a): (s, mkprimitive(s, a, b)), PM)


def setup_ties_environment():
    env = setup_environment()
    env.putall(ties_primitive_procedures())
    return env
