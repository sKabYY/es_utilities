#

from common.container import Table, Buckets


def _format(origin_data):
    return Table(origin_data)


def hits_sources(formatted_data):

    def get_source_or_fields(doc):
        try:
            return doc._source
        except AttributeError:
            return doc.fields

    return map(get_source_or_fields, formatted_data.hits.hits)


def facet_terms(name, formatted_data):
    '''
        return formatted_data[name]['terms']
    '''
    return formatted_data.facets[name].terms


def facet_entries(name, formatted_data):
    '''
        return formatted_data[name]['entries']
    '''
    return formatted_data.facets[name].entries


def groupby_func(data, func):
    '''
    <data> is a list of Table
    <func> is a function which maps a Table to a value
    '''
    buckets = Buckets()
    for e in data:
        buckets.put(func(e), e)
    return map(buckets.get, sorted(buckets))


def groupby(data, field):
    '''
    <data> is a list of Table or dictionary which has key <field>.
    '''
    return groupby_func(data, lambda e: e[field])


def number(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def difference(data, field, use_the_latter=False):
    '''
    <data> is a list of Table or dictionary
    which has key <field> and the value for key <field> is a number.
    '''
    def __diff(prev, curr):
        n_d = number(curr[field]) - number(prev[field])
        if use_the_latter:
            d = dict(curr)
        else:
            d = dict(prev)
        d[field] = n_d
        return d

    n = len(data)
    if n <= 1:
        return []
    else:
        prev = data[0]
        res = []
        for i in xrange(1, n):
            curr = data[i]
            res.append(__diff(prev, curr))
            prev = curr
        return res
