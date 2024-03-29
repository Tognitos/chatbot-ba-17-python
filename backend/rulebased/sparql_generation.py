# -*- coding: utf-8 -*-

"""
Sparql generation code.
"""

from quepy import settings
from quepy.dsl import IsRelatedTo
from quepy.expression import isnode
from quepy.encodingpolicy import assert_valid_encoding
from imdb_sparql.movies import MyExtra
import imdb_sparql
import logging

_indent = u"  "

logger = logging.getLogger('quepy')


def escape(string):
    string = unicode(string)
    string = string.replace("\n", "")
    string = string.replace("\r", "")
    string = string.replace("\t", "")
    string = string.replace("\x0b", "")
    if not string or any([x for x in string if 0 < ord(x) < 31]) or \
            string.startswith(":") or string.endswith(":"):
        message = "Unable to generate sparql: invalid nodes or relation"
        raise ValueError(message)
    return string


def adapt(x):
    if isnode(x):
        x = u"?x{}".format(x)
        return x
    if isinstance(x, basestring):
        assert_valid_encoding(x)
        if x.startswith(u"?"):
            return x
        if x.startswith(u"\"") or ":" in x:
            return x
        return u'"{}"'.format(x)
    return unicode(x)


def expression_to_sparql(e, full=False):
    logger.debug('MONKEY MONKEY')
    template = u"{preamble}\n" +\
               u"SELECT DISTINCT {select} WHERE {{\n" +\
               u"{expression}\n" +\
               u"}} {orderby}\n"


    if e.get_head() == "*":
        select = u"*"
    else:
        head = adapt(e.get_head())
        if full:
            select = u"*"
        else:
            select = head

    orderby = u""

    y = 0
    xs = []
    for node in e.iter_nodes():
        for relation, dest in e.iter_edges(node):
            # It would have been better with isinstance(relation, MyExtra) but
            # for some reasons it doesn't seem to work
            if relation.__class__.__name__ == 'MyExtra':
                xs.append(_indent + relation.extra)
            elif relation.__class__.__name__ == 'OrderBy':
                orderby = relation.text
            else:
                if relation is IsRelatedTo:
                    relation = u"?y{}".format(y)
                    y += 1
                xs.append(triple(adapt(node), relation, adapt(dest),
                          indentation=1))
    sparql = template.format(preamble=settings.SPARQL_PREAMBLE,
                             select=select,
                             expression=u"\n".join(xs),
                             orderby=orderby)
    return select, sparql


def triple(a, p, b, indentation=0):
    a = escape(a)
    b = escape(b)
    p = escape(p)
    s = _indent * indentation + u"{0} {1} {2}."
    return s.format(a, p, b)
