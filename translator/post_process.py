#

from common.container import Table, Slots


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
    return formatted_data.facets[name].terms


def facet_entries(name, formatted_data):
    return formatted_data.facets[name].entries


def groupby(data, field):
    '''
    <data> is a list of Table or dictionary which has key <field>.
    '''
    slots = Slots()
    for e in data:
        slots.put(e[field], e)
    return map(slots.get, sorted(slots))


def difference(data, field, use_the_latter=False):
    '''
    <data> is a list of Table or dictionary
    which has key <field> and the value for key <field> is a number.
    '''
    def __diff(prev, curr):
        n_d = curr[field] - prev[field]
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
