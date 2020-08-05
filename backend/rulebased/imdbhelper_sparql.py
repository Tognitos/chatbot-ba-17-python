# coding: utf-8
import quepy
from models import Attachment
from SPARQLWrapper import SPARQLWrapper, JSON

idk = Attachment('text', 'I do not know how to answer')

class IMDB_SPARQL(object):

    def __init__(self, url):
        self.dbbase = quepy.install("imdb_sparql")
        self.connection = None
        self.sparql = SPARQLWrapper(url)

    def query(self, question, session_id, history_object):
        # get the most probable query
        target, query, metadata = self.dbbase.get_query(question)

        print('query')
        print(query)

        print('metadata')
        print(metadata)

        if isinstance(metadata, tuple):
            query_type = metadata[0]
            metadata = metadata[1]
        else:
            query_type = metadata
            metadata = None

        if query is None:
            print ("Query not generated :(\n")
            return None, (target, query, metadata)

        if target.startswith("?"):
            target = target[1:]

        # add limit to query
        query = "%s limit %d" % (query, 5)

        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()

        if not results["results"]["bindings"]:
            print ("No answer found :(")
            return None, (target, query, metadata)


        print('Target result')
        # Results filtered for the target of the query (works with just one target)
        target_results = []
        for result in results["results"]["bindings"]:
            tmp = result[target]["value"]
            target_results.append(tmp)

        attachment = Attachment('text', target_results[0]) if len(results) == 1 else\
                     Attachment('list', target_results)

        return attachment, (target, query, metadata)
