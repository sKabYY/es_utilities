#

from common.table import table


def _format(origin_data):
    return table(origin_data)


def hits_sources(formatted_data):
    return map(lambda doc: doc._source, formatted_data.hits.hits)


def facet_terms(name, formatted_data):
    return formatted_data.facets[name].terms


def facet_entries(name, formatted_data):
    return formatted_data.facets[name].entries
