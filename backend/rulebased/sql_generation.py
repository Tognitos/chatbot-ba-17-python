# -*- coding: utf-8 -*-

"""
SQL generation code.
"""

from quepy import settings
from quepy.dsl import IsRelatedTo
from quepy.expression import isnode
from quepy.encodingpolicy import assert_valid_encoding

_indent = u"  "


def escape(string):
    string = unicode(string)
    string = string.replace("\n", "")
    string = string.replace("\r", "")
    string = string.replace("\t", "")
    string = string.replace("\x0b", "")
    if not string or any([x for x in string if 0 < ord(x) < 31]) or \
            string.startswith(":") or string.endswith(":"):
        message = "Unable to generate sql: invalid nodes or relation"
        raise ValueError(message)
    return string


def adapt(x):
    if isnode(x):
        x = u"?x{}".format(x)
        return x
    if isinstance(x, basestring):
        assert_valid_encoding(x)
        if x.startswith(u"\"") or ":" in x:
            return x
        return u'"{}"'.format(x)
    return unicode(x)


def expression_to_sql(e, full=False):
    template = u"SELECT  {select} from {table} WHERE " +\
               u"{expression}" +\
               u";"
    head = e.get_head()
    if full:
        select = u"*"
    else:
        select = head
    y = 0
    # xs = []
    # for node in e.iter_nodes():
    #     for relation, dest in e.iter_edges(node):
    #         if relation is IsRelatedTo:
    #             relation = u"?y{}".format(y)
    #             y += 1
    #         xs.append(triple(adapt(node), relation, adapt(dest),
    #                   indentation=1))
    # expressions=translate_sparql_to_sql(xs)

    expression=e.nodes[0]
    if len(e.tables)==1:
        sql = template.format(
                                 select=select,
                              table=e.tables[0],
                                 expression=expression)
    else:
        sql=[]
        for i in range(len(e.tables)):
            sql.append(template.format(
                                 select=select,
                              table=e.tables[i],
                                 expression=expression))
    return select, sql


def triple(a, p, b, indentation=0):
    a = escape(a)
    b = escape(b)
    p = escape(p)
    s = _indent * indentation + u"{0} {1} {2}."
    return s.format(a, p, b)
