#

from common.container import Table, Buckets


def _format(origin_data):
    return Table(origin_data)


def hits_additional_info(formatted_data):
    '''
    total
    '''
    addi = Table()
    addi.total = formatted_data.hits.total
    return addi


def hits_sources(formatted_data):
    '''
        return formatted_data['hits']['hits']['_source']
        OR
        return formatted_data['hits']['hits']['fields']
    '''

    def get_source_or_fields(doc):
        try:
            return doc._source
        except AttributeError:
            try:
                return doc.fields
            except AttributeError:
                return {}

    return map(get_source_or_fields, formatted_data.hits.hits)


def facet_terms_additional_info(name, formatted_data):
    '''
    total
    other
    missing
    '''
    addi = Table()
    addi.total = formatted_data.facets[name].total
    addi.other = formatted_data.facets[name].other
    addi.missing = formatted_data.facets[name].missing
    return addi


def facet_terms(name, formatted_data):
    '''
        return formatted_data['facets'][name]['terms']
    '''
    return formatted_data.facets[name].terms


def facet_entries(name, formatted_data):
    '''
        return formatted_data['facets'][name]['entries']
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


def groupby_field(data, field):
    '''
    <data> is a list of Table or dictionary which has key <field>.
    '''
    return groupby_func(data, lambda e: e[field])


def number(s):
    '''
    Translate string <s> to an integer or a float.
    '''
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
