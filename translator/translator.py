#
#
#

# Conditions ##############################################

import pprint


# Base class
class Condition(object):
    def __str__(self):
        return pprint.pformat(self.to_dict())


class NilCondition(Condition):
    '''
    DO NOT USE THIS CLASS!!!
    '''
    def to_dict(self):
        return {'query_string': {'query': '*'}}


# Atom:
class AtomCondition(Condition):
    '''
    Make sure that the atom condition can be used in query.
    NOTE: Some condition may only be used in filter (I guess).
    '''
    def is_atom(self):
        return True


class Equal(AtomCondition):
    '''
    Need the field is not analyzed.
    '''
    def __init__(self, field, value):
        self.field = field
        self.value = value

    def to_dict(self):
        return {'term': {self.field: self.value}}


class Prefix(AtomCondition):
    def __init__(self, field, value):
        self.field = field
        self.value = value

    def to_dict(self):
        return {'prefix': {self.field: self.value}}


class Range(AtomCondition):
    def __init__(self, field, start, end):
        self.field = field
        self.start = start
        self.end = end

    def to_dict(self):
        return {'range': {
            self.field: {
                'gte': self.start,
                'lt': self.end,
                }
        }}


# Not Atom:
class NotAtomCondition(Condition):
    def is_atom(self):
        return False


class And(NotAtomCondition):
    def __init__(self, conditions):
        '''
        "conditions" is a list of Condition
        '''
        self.conditions = conditions

    def to_dict(self):
        '''
        Return {
            "and": [
                condition1,
                condition2,
                condition3,
                ...
            ]
        }
        '''
        l = []
        for condition in self.conditions:
            l.append(condition.to_dict())
        return {'and': l}


class Or(NotAtomCondition):
    def __init__(self, conditions):
        '''
        "conditions" is a list of Condition
        '''
        self.conditions = conditions

    def to_dict(self):
        '''
        Return {
            "or": [
                condition1,
                condition2,
                condition3,
                ...
            ]
        }
        '''
        l = []
        for condition in self.conditions:
            l.append(condition.to_dict())
        return {'or': l}


class Not(NotAtomCondition):
    def __init__(self, condition):
        '''
        "condition" is a instance of Condition (NOT LIST)
        '''
        self.condition = condition

    def to_dict(self):
        return {'not': self.condition.to_dict()}

###########################################################


# ESQuery Type ############################################
class ESQueryType(object):
    def is_facet(self):
        return False

    def is_hits(self):
        return False


class Hits(ESQueryType):
    def __init__(self, size, fields=[], condition=None, sort=None):
        '''
        parameters:
            size: integer
            fields: list of string, optional, default all fields
            condition: Condition, optional
            sort: a tuple with two elements,
                  the first is a field and the other is a boolean, optional
        '''
        self.size = size
        self.fields = fields
        self.condition = condition
        self.sort = sort

    def is_hits(self):
        return True

    def to_dict(self):
        def sort_to_dict(sort):
            field = sort[0]
            reverse = sort[1]
            if reverse:
                dire = 'desc'
            else:
                dire = 'asc'
            d = {}
            d[field] = dire
            return d

        d = {}
        d['size'] = self.size
        if self.fields != []:
            d['fields'] = self.fields
        if self.condition is not None:
            d['filter'] = self.condition.to_dict()
        if self.sort is not None:
            d['sort'] = sort_to_dict(self.sort)
        return d


class Facet(ESQueryType):
    def __init__(self, name, condition):
        self.name = name
        self.condition = condition

    def is_facet(self):
        return True

    def _add_facets_filter(self, d):
        '''
        This function is called by its subclass to add a facet_filter
        '''
        if self.condition is not None:
            d['facet_filter'] = self.condition.to_dict()
        return d


class Terms(Facet):
    ES_FACET_TYPE = 'terms'

    def __init__(self, name, field, size, condition=None):
        super(Terms, self).__init__(name, condition)
        self.field = field
        self.size = size

    def to_dict(self):
        '''
        Return an ES facet dictionary.
        If self.condition is None then return dictionary:
        {
            "terms": {
                "field": self.field,
                "size": self.size,
                "order": "count",
            }
        }
        else return dictionary:
        {
            "terms": {
                "field": self.field,
                "size": self.size,
                "order": "count",
            },
            "facet_filter": self.condition.to_dict()
        }
        '''
        return self._add_facets_filter({
            Terms.ES_FACET_TYPE: {
                'field': self.field,
                'size': self.size,
                'order': 'count',
            }
        })


class Histogram(Facet):
    ES_FACET_TYPE = 'date_histogram'

    def __init__(self, name, timestamp_field, interval, condition=None):
        super(Histogram, self).__init__(name, condition)
        self.interval = interval
        self.ts_field = timestamp_field

    def to_dict(self):
        '''
        Return an ES facet dictionary.
        If self.condition is None then return dictionary:
        {
            "date_histogram": {
                "key_field": timestamp_field,
                "interval": interval,
            }
        }
        else return dictionary:
        {
            "date_histogram": {
                "key_field": timestamp_field,
                "interval": interval,
            },
            "facet_filter": self.condition.to_dict()
        }
        '''
        return self._add_facets_filter({
            Histogram.ES_FACET_TYPE: {
                'key_field': self.ts_field,
                'interval': self.interval,
            }
        })

###########################################################


def translate(hits, facets=[], conditions=[]):
    '''
    <facets> is a list of Facet
    <conditions> is a list of Condition
    '''
    def select_a_query_condition(conditions):
        qcond = NilCondition()
        for condition in conditions:
            if condition.is_atom():
                qcond = condition
                break
        rest = [c for c in conditions if c != qcond]
        return qcond, rest

    def conditions_to_dict(conditions):
        qcond, rest = select_a_query_condition(conditions)
        if len(rest) == 0:
            return qcond.to_dict()
        else:
            if len(rest) > 1:
                rest_cond = And(rest)
            else:
                rest_cond = rest[0]
            return {
                'filtered': {
                    'query': qcond.to_dict(),
                    'filter': rest_cond.to_dict(),
                }}

    d = {}
    d['query'] = conditions_to_dict(conditions)
    if len(facets) > 0:
        fsd = {}
        for facet in facets:
            fsd[facet.name] = facet.to_dict()
        d['facets'] = fsd
    d.update(hits.to_dict())
    return d
