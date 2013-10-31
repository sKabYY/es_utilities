import elasticsearch as ES

from translator.translator import (
    translate,
    Equal, Range, Prefix,
    And, Or, Not,
    Hits, Terms, Histogram
)
from translator.post_process import (
    _format,
    hits_additional_info, hits_sources,
    facet_terms_additional_info, facet_terms,
    facet_entries,
)
from interp.tilib import (
    ge2nd, le2nd, eq2nd, inrange,
    setup_environment,
)
from interp.titype import (
    mkvoid, isvoid,
    mkprimitive,
)


__global_url = 'localhost'
__global_port = '9200'
__global_index = '*'
__global_doc_type = mkvoid()


def connect(url, port):
    r'''(connect url port): <url> and <port> are strings.'''
    global __global_url
    global __global_port
    __global_url = url
    __global_port = port
    return mkvoid()


def set_index(index):
    r'''(set-index! index): <index> is a string.'''
    global __global_index
    __global_index = index
    return mkvoid()


def get_index():
    r'''(get-index): Returns the index currently in use.'''
    return __global_index


def set_doc_type(doc_type):
    r'''(set-doc-type! doc-type): <doc-type> is a string.'''
    global __global_doc_type
    __global_doc_type = doc_type
    return mkvoid()


def get_doc_type():
    r'''(get-doc-type): Returns the doc type currently in use.'''
    return __global_doc_type


def prompt():
    p = '%s:%s/%s' % (
        __global_url, __global_port, __global_index,
    )
    if isvoid(__global_doc_type):
        return p
    else:
        return '%s/%s' % (p, __global_doc_type)


def translate_wrapper(hits, facets, conditions):
    if not isinstance(conditions, list):
        conditions = [conditions]
    return translate(hits, facets, conditions)


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


# response types ##########################################
import pprint


class ResponseList(list):
    def __init__(self, initdata, additional_info=None):
        r'''
        <initdata> is a list-like object (an iterable) and
        <additional> is a Table.
        '''
        self.extend(initdata)
        self.additional_info = additional_info

    def __str__(self):
        data_str = pprint.pformat(self)
        if self.additional_info is None:
            return data_str
        else:
            addi_str = pprint.pformat(self.additional_info)
            return '%s\n\nAdditional info:\n%s' % (data_str, addi_str)


# functions for elasticsearch #############################


def es_search(post_data):
    r'''(es_search post_data):
<post_data> is a translated data.
This function returns the origin response'''
    es = ES.Elasticsearch([{
        'host': __global_url,
        'post': __global_port,
    }])
    kwargs = {
        'index': __global_index,
        'body': post_data,
    }
    if not isvoid(__global_doc_type):
        kwargs['doc_type'] = __global_doc_type
    return _format(es.search(**kwargs))


def Sort(field, reverse=False):
    r'''Used Only in translate-hits or search-hits'''
    return (field, reverse)


def translate_hits(*args):
    r'''args: [size, fields, conditions, sort]'''
    size, fields, conditions, sort = add_default(args, [10, [], [], None])
    h = Hits(size, fields,  None, sort)
    post_data = translate_wrapper(h, [], conditions)
    return post_data


def search_hits(*args):
    orig = es_search(translate_hits(*args))
    data = hits_sources(orig)
    addi = hits_additional_info(orig)
    return ResponseList(data, addi)


__GLOBAL_TERMS_TAGS = '__terms__'


def translate_terms(*args):
    r'''args: [field, size, conditions]'''
    field, size, conditions = add_default(args, [None, 10, []])
    t = Terms(__GLOBAL_TERMS_TAGS, field, size)
    post_data = translate_wrapper(Hits(0), [t], conditions)
    return post_data


def search_terms(*args):
    orig = es_search(translate_terms(*args))
    data = facet_terms(__GLOBAL_TERMS_TAGS, orig)
    addi = facet_terms_additional_info(__GLOBAL_TERMS_TAGS, orig)
    return ResponseList(data, addi)


__GLOBAL_HISTOGRAM_TAGS = '__histogram__'


def translate_histogram(*args):
    r'''args: [timestamp_field, interval, conditions]'''
    ts_field, interval, conditions = add_default(args, [None, 'hour', []])
    h = Histogram(__GLOBAL_HISTOGRAM_TAGS, ts_field, interval)
    post_data = translate_wrapper(Hits(0), [h], conditions)
    return post_data


def search_histogram(*args):
    orig = es_search(translate_histogram(*args))
    data = facet_entries(__GLOBAL_HISTOGRAM_TAGS, orig)
    # histogram has no additional info
    return ResponseList(data)


# functions of datetime ###################################


import common.timeutils as tt
from datetime import timedelta


def now():
    r'''(now): Returns current datetime in UTC timezone.'''
    return tt.get_now()


def hours(n):
    r'''(hours n): Returns timedelta(hours=n).'''
    return timedelta(hours=n)


def days(n):
    r'''(days n): Returns timedelta(days=n).'''
    return timedelta(days=n)


###########################################################


def ties_primitive_procedures():
    PM = [
        # environment
        ('connect!', connect, eq2nd(2)),
        ('set-index!', set_index, eq2nd(1)),
        ('get-index', get_index, eq2nd(0)),
        ('set-doc-type!', set_doc_type, eq2nd(1)),
        ('get-doc-type', get_doc_type, eq2nd(0)),
        # conditions
        ('Equal', Equal, eq2nd(2)),
        ('Range', Range, eq2nd(3)),
        ('Prefix', Prefix, eq2nd(2)),
        ('And', lambda *conds: And(conds), ge2nd(1)),
        ('Or', lambda *conds: Or(conds), ge2nd(1)),
        ('Not', Not, eq2nd(1)),
        # translate and search
        ('Sort', Sort, inrange(1, 2)),
        ('origin-search', es_search, eq2nd(1)),
        ('translate-hits', translate_hits, le2nd(4)),
        ('search-hits', search_hits, le2nd(4)),
        ('translate-terms', translate_terms, inrange(1, 4)),
        ('search-terms', search_terms, inrange(1, 4)),
        ('translate-histogram', translate_histogram, inrange(1, 3)),
        ('search-histogram', search_histogram, inrange(1, 3)),
        # datetime
        ('now', now, eq2nd(0)),
        ('hours', hours, eq2nd(1)),
        ('days', days, eq2nd(1)),
    ]
    return map(lambda (s, b, a): (s, mkprimitive(s, a, b)), PM)


def setup_ties_environment():
    env = setup_environment()
    env.putall(ties_primitive_procedures())
    return env
