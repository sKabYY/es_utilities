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
    _any, ge_than, eq_to, inrange,
    setup_environment,
    check_error, raise_error,
)
from interp.titype import (
    mkvoid, isvoid,
    mkfalse, istrue,
    issymbol, symbol_tostring,
    mkprimitive,
)
from common.container import Table


buildin_values = Table()

buildin_values.url = 'localhost'
buildin_values.port = '9200'
buildin_values.index = '*'
buildin_values.doc_type = mkvoid()


def tiesproc(f):
    '''
    This decorator does nothing. It just tags the functions which are exported.
    '''
    return f


@tiesproc
def connect(url, port):
    r'''(connect url port): <url> and <port> are strings.'''
    buildin_values.url = url
    buildin_values.port = port
    return mkvoid()


@tiesproc
def set_index(index):
    r'''(set-index! index): <index> is a string.'''
    buildin_values.index = index
    return mkvoid()


@tiesproc
def get_index():
    r'''(get-index): Returns the index currently in use.'''
    return buildin_values.index


@tiesproc
def set_doc_type(doc_type):
    r'''(set-doc-type! doc-type): <doc-type> is a string.'''
    buildin_values.doc_type = doc_type
    return mkvoid()


@tiesproc
def get_doc_type():
    r'''(get-doc-type): Returns the doc type currently in use.'''
    return buildin_values.doc_type


def prompt():
    p = '%s:%s/%s' % (
        buildin_values.url, buildin_values.port, buildin_values.index,
    )
    if isvoid(buildin_values.doc_type):
        return p
    else:
        return '%s/%s' % (p, buildin_values.doc_type)


def translate_wrapper(hits, facets, conditions):
    if not isinstance(conditions, list):
        conditions = [conditions]
    return translate(hits, facets, conditions)


def has_symbol(lst):
    r'''
    Returns whether <lst> has symbol.
    '''
    assert isinstance(lst, (list, tuple))
    return any(map(issymbol, lst))


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


@tiesproc
def es_search(post_data):
    r'''(es_search post_data):
<post_data> is a translated data.
This function returns the origin response'''
    es = ES.Elasticsearch([{
        'host': buildin_values.url,
        'post': buildin_values.port,
    }])
    kwargs = {
        'index': buildin_values.index,
        'body': post_data,
    }
    if not isvoid(buildin_values.doc_type):
        kwargs['doc_type'] = buildin_values.doc_type
    return _format(es.search(**kwargs))


class MissingArgument(object):
    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return '<MissingArgument %s>' % repr(self.msg)

    def __str__(self):
        return self.msg


def parse_args(template, *args):

    def get_options_from_arguments(lst):
        n = len(lst)
        i = 0
        res = []
        while i < n:
            option = lst[i]
            check_error(
                issymbol(option),
                'Expect a option but get %s' % option)
            option = '\'%s' % symbol_tostring(option)
            check_error(
                i + 1 < n,
                'Missing parameter after %s' % option)
            param = lst[i + 1]
            res.append((option, param))
            i += 2
        return res

    def default_kwargs(template):
        d = {}
        for _, key, value in template:
            d[key] = get_buildin_value_or_self(value)
        return d

    def find_argument_name(template, option):
        for option_name, arg_name, _ in template:
            if option == option_name:
                return arg_name
        raise_error('Unknown option %s' % option)

    def add_default(args, default_list):
        res = list(args)
        start = len(res)
        end = len(default_list)
        while start < end:
            res.append(default_list[start])
            start += 1
        return res

    def check_missing_one(arg):
        check_error(not isinstance(arg, MissingArgument),
                    str(arg))

    def check_missing(args):
        if isinstance(args, list):
            for arg in args:
                check_missing_one(arg)
        elif isinstance(args, dict):
            for arg in args.values():
                check_missing_one(arg)
        else:
            assert False

    if has_symbol(args):
        options = get_options_from_arguments(args)
        translate_args = default_kwargs(template)
        for option, param in options:
            arg_name = find_argument_name(template, option)
            translate_args[arg_name] = param
    else:
        translate_args = add_default(
            args, map(lambda t: get_buildin_value_or_self(t[2]), template))
    check_missing(translate_args)
    return translate_args


def unpack_and_translate(do_translate_func, translate_args):
    if isinstance(translate_args, list):
        return do_translate_func(*translate_args)
    elif isinstance(translate_args, dict):
        return do_translate_func(**translate_args)
    else:
        assert False


# environment for conditions ###
buildin_values.default_conditions = []
###


# hits ###


@tiesproc
def Sort(field, reverse=mkfalse()):
    r'''Used Only in translate-hits or search-hits'''
    return (field, istrue(reverse))


# environment for hits ###
buildin_values.hits_default_size = 10
buildin_values.hits_default_fields = []
buildin_values.hits_default_sort = None
###


def hits_parse_args(*args):
    r'''
    Two styles of arguments:
        1. argument style:
            (search-hits size fields conditions sort)
        2. option style:
            (search-hits 's size 'f fields 'c conditions 'sort sort)
    All arguments are optional.
    '''
    return parse_args(get_template('hits'), *args)


def do_translate_hits(size, fields, conditions, sort):
    h = Hits(size, fields, None, sort)
    post_data = translate_wrapper(h, [], conditions)
    return post_data


@tiesproc
def translate_hits(*args):
    return unpack_and_translate(
        do_translate_hits,
        hits_parse_args(*args))


@tiesproc
def search_hits(*args):
    orig = es_search(translate_hits(*args))
    data = hits_sources(orig)
    addi = hits_additional_info(orig)
    return ResponseList(data, addi)


# terms ###
__GLOBAL_TERMS_TAGS = '__terms__'

# environment for terms ###
buildin_values.terms_default_size = 10
###


def terms_parse_args(*args):
    r'''
    Two styles of arguments:
        1. argument style:
            (search-terms field size conditions)
        2. option style:
            (search-hits 'f field 's size 'c conditions)
    <size> and <conditions> are optional.
    '''
    return parse_args(get_template('terms'), *args)


def do_translate_terms(field, size, conditions):
    t = Terms(__GLOBAL_TERMS_TAGS, field, size)
    post_data = translate_wrapper(Hits(0), [t], conditions)
    return post_data


@tiesproc
def translate_terms(*args):
    return unpack_and_translate(
        do_translate_terms,
        terms_parse_args(*args))


@tiesproc
def search_terms(*args):
    orig = es_search(translate_terms(*args))
    data = facet_terms(__GLOBAL_TERMS_TAGS, orig)
    addi = facet_terms_additional_info(__GLOBAL_TERMS_TAGS, orig)
    return ResponseList(data, addi)


# histogram ###
__GLOBAL_HISTOGRAM_TAGS = '__histogram__'

# environment for histogram ###
buildin_values.histogram_default_timestamp_field = MissingArgument(
    'Missing argument "timestamp_field"')
buildin_values.histogram_default_interval = 'hour'
###


def histogram_parse_args(*args):
    r'''
    Two styles of arguments:
        1. argument style:
            (search-histogram timestamp_field interval conditions)
        2. option style:
            (search-histogram 't timestamp_field 'i interval 'c conditions)
    <interval> and <conditions> are optional.
    <timestamp_field> can be optional.
    '''
    return parse_args(get_template('histogram'), *args)


def do_translate_histogram(timestamp_field, interval, conditions):
    h = Histogram(__GLOBAL_HISTOGRAM_TAGS, timestamp_field, interval)
    post_data = translate_wrapper(Hits(0), [h], conditions)
    return post_data


@tiesproc
def translate_histogram(*args):
    return unpack_and_translate(
        do_translate_histogram,
        histogram_parse_args(*args))


@tiesproc
def search_histogram(*args):
    orig = es_search(translate_histogram(*args))
    data = facet_entries(__GLOBAL_HISTOGRAM_TAGS, orig)
    # histogram has no additional info
    return ResponseList(data)


__global_all_templates = [
    ('hits', [
        ('\'s', 'size', 'hits_default_size'),
        ('\'f', 'fields', 'hits_default_fields'),
        ('\'c', 'conditions', 'default_conditions'),
        ('\'sort', 'sort', 'hits_default_sort')]),
    ('terms', [
        ('\'f', 'field', MissingArgument('Missing argument "field"')),
        ('\'s', 'size', 'terms_default_size'),
        ('\'c', 'conditions', 'default_conditions')]),
    ('histogram', [
        ('\'t', 'timestamp_field', 'histogram_default_timestamp_field'),
        ('\'i', 'interval', 'histogram_default_interval'),
        ('\'c', 'conditions', 'default_conditions')]),
]


@tiesproc
def set_condition(conditions):
    buildin_values.default_conditions = conditions
    return mkvoid()


@tiesproc
def set_hits_size(size):
    buildin_values.hits_default_size = size
    return mkvoid()


@tiesproc
def set_hits_fields(fields):
    buildin_values.hits_default_fields = fields
    return mkvoid()


@tiesproc
def set_hits_sort(sort):
    buildin_values.hits_default_sort = sort
    return mkvoid()


@tiesproc
def set_terms_field(field):
    buildin_values.terms_default_field = field
    return mkvoid()


@tiesproc
def set_terms_size(size):
    buildin_values.terms_default_size = size
    return mkvoid()


@tiesproc
def set_histogram_timestamp_field(timestamp_field):
    buildin_values.histogram_default_timestamp_field = timestamp_field
    return mkvoid()


@tiesproc
def set_histogram_interval(interval):
    buildin_values.histogram_default_interval = interval
    return mkvoid()


def get_template(name):
    for n, template in __global_all_templates:
        if n == name:
            return template
    assert False


def get_buildin_value_or_self(key):
    if type(key) == str:
        return buildin_values[key]
    else:
        return key


@tiesproc
def show_default_args(*keys):
    def try_get_symbol_content(v):
        if issymbol(v):
            return v.content
        else:
            return v

    if len(keys) == 0:
        pred = lambda x: True
    else:
        keys = map(try_get_symbol_content, keys)
        pred = lambda x: x in keys

    def print_template(indent, template):
        for option, name, key in template:
            value = get_buildin_value_or_self(key)
            print '%s%s\t%s\t%s' % (indent, option, name, repr(value))

    for name, template in __global_all_templates:
        if pred(name):
            print name
            print_template(' ', template)
            print
    return mkvoid()


# functions of datetime ###################################


import common.timeutils as tt
from datetime import timedelta


@tiesproc
def now():
    r'''(now): Returns current datetime in UTC timezone.'''
    return tt.get_now()


@tiesproc
def hours(n):
    r'''(hours n): Returns timedelta(hours=n).'''
    return timedelta(hours=n)


@tiesproc
def days(n):
    r'''(days n): Returns timedelta(days=n).'''
    return timedelta(days=n)


###########################################################


def ties_primitive_procedures():
    PM = [
        # environment
        ('connect!', connect, eq_to(2)),
        ('set-index!', set_index, eq_to(1)),
        ('get-index', get_index, eq_to(0)),
        ('set-doc-type!', set_doc_type, eq_to(1)),
        ('get-doc-type', get_doc_type, eq_to(0)),
        # conditions
        ('Equal', Equal, eq_to(2)),
        ('Range', Range, eq_to(3)),
        ('Prefix', Prefix, eq_to(2)),
        ('And', lambda *conds: And(conds), ge_than(1)),
        ('Or', lambda *conds: Or(conds), ge_than(1)),
        ('Not', Not, eq_to(1)),
        # translate and search
        ('Sort', Sort, inrange(1, 2)),
        ('origin-search', es_search, eq_to(1)),
        ('translate-hits', translate_hits, _any),
        ('search-hits', search_hits, _any),
        ('translate-terms', translate_terms, _any),
        ('search-terms', search_terms, _any),
        ('translate-histogram', translate_histogram, _any),
        ('search-histogram', search_histogram, _any),
        # default arguments
        ('show-default-args', show_default_args, _any),
        ('set-condition!', set_condition, eq_to(1)),
        ('set-hits-size!', set_hits_size, eq_to(1)),
        ('set-hits-fields!', set_hits_fields, eq_to(1)),
        ('set-hits-sort!', set_hits_sort, eq_to(1)),
        ('set-terms-field!', set_terms_field, eq_to(1)),
        ('set-terms-size!', set_terms_size, eq_to(1)),
        ('set-histogram-timestamp-field',
         set_histogram_timestamp_field, eq_to(1)),
        ('set-histogram-interval', set_histogram_interval, eq_to(1)),
        # datetime
        ('now', now, eq_to(0)),
        ('hours', hours, eq_to(1)),
        ('days', days, eq_to(1)),
    ]
    return map(lambda (s, b, a): (s, mkprimitive(s, a, b)), PM)


def setup_ties_environment():
    env = setup_environment()
    env.putall(ties_primitive_procedures())
    return env
