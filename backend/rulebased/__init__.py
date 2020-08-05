import quepy
import sys
import os

# monkey patch to add sql generation
from quepy.mql_generation import generate_mql
from quepy.dot_generation import expression_to_dot
from sparql_generation import expression_to_sparql
from sql_generation import expression_to_sql

def get_code_(expression, language):
    if language == "sparql":
        return expression_to_sparql(expression)
    elif language == "sql":
        return expression_to_sql(expression)
    elif language == "dot":
        return expression_to_dot(expression)
    elif language == "mql":
        return generate_mql(expression)
    else:
        message = u"Language '{}' is not supported"
        raise ValueError(message.format(language))

quepy.generation.get_code = get_code_

# add the current directory rulebased/ to the path so that quepy will be able
# to find and install imdb/dbpedia
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))

# add the parent directory to the sys path so that the rulebased module can
# import and mysqlhelper
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
