from context import Entity, SPO, LiteralObject, Context, WildcardPredicate
from graph_metadata import *

PREFIXES = ['PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>' ,\
            'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>' ,\
            'PREFIX dbp-owl: <http://dbpedia.org/ontology/>' ,\
            'PREFIX dbpediaowl: <http://dbpedia.org/ontology/>' ,\
            'PREFIX dbpprop: <http://dbpedia.org/property/>' ,\
            'PREFIX foaf: <http://xmlns.com/foaf/0.1/>' ,\
            'PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>' ,\
            'PREFIX fo: <http://www.w3.org/1999/XSL/Format#>' ,\
            'PREFIX fn: <http://www.w3.org/2005/xpath-functions#>' ,\
            'PREFIX ns:   <http://example.com/ns#>']


"""
executes intent with the provided entities
returns resultset, context
"""
# TODO: this shouldn't be here
def execute_intent(intent, entities, properties, literal_objects):
    if intent == 'list_movies_of_year':
        results = ["Anon. Trailer Music II", "Box", "Coconut Hero", "Want It", "The Last Orthodontist"]
        # we know the intent so we know the context already
        context = demo_listmovies_context()

        print('list movies context as sparql')
        sparql = generate_sparql_from_context(context)
        print(sparql)

        #TODO: execute sparql query

        return results, context
    elif intent == 'plot_of_film':
        results = ["Anon. Trailer Music II", "Box", "Coconut Hero", "Want It", "The Last Orthodontist"]
        # we know the intent so we know the context already
        context = demo_plot_of_film_context(literal_objects[0])
        sparql = generate_sparql_from_context(context)
        print(sparql)

        #TODO: execute sparql query

        return results, context

    return [], None



"""
generates sparql query by cycling through the context object and joining their relationships
params:
    - context: Context
    - form: 'SELECT' | 'ASK' . If we want query results or just test if a solution exists. Default 'SELECT'
returns the sparql query
"""
def generate_sparql_from_context(context, form='SELECT', prefixes=True, modifier=None):
    query_prefixes = "\n".join(PREFIXES) if prefixes else ""

    # subject has always the ?, predicate never and object sometimes
    query_spo_template = "?%s %s %s."

    # tmp line (subject-predicate-object)
    query_line = None

    # query select
    query_select_columns = ""

    # list of columns to be returned to facilitate the parsing of the RESPONSE
    select_columns = []

    # the whole generated query
    query_body = ""
    sparql_objects = dict()   
    for entity in context.all_entities:
        # sparqlify the type constraint for the entity
        query_body += ('\n' + query_spo_template % ( get_sparql_var_name(entity), \
                                                'rdf:type', \
                                                entity.get_rdftype())
                )
     
        
        # sparqlify all the relationships
        for spo in entity.spos:
            print spo.p.__dict__
            print spo
            object_as_sparql = None

            # object not specified, it means its a target of the user's query
            if spo.o == None:
                # e.g. ?Actor_foaf_name
                object_as_sparql = '?%s_%s_%s_%s' % \
                                (spo.p.prop_domain, \
                                spo.s.query_id, \
                                spo.p.prop_prefix, \
                                spo.p.prop_name)
                select_columns.append(object_as_sparql)
                query_select_columns += " " + object_as_sparql
            # object is a literal
            elif isinstance(spo.o, LiteralObject):

                # add quotes around object if it is a string literal
                if spo.o.literal_type == 'string':
                    object_as_sparql = quote_string(spo.o.value)
                # do not add quotes around object otherwise
                else:
                    object_as_sparql = spo.o.value

            # object not a literal, use the ?
            else:
                object_as_sparql = '?%s' % get_sparql_var_name(spo.o)


            sparql_objects[spo] = object_as_sparql
            query_line = query_spo_template % (get_sparql_var_name(spo.s), \
                                               get_sparql_var_name(spo.p), \
                                               object_as_sparql)

            query_body += ('\n' + query_line)




    if form == 'SELECT':
        query_template = "%s \n SELECT %s WHERE { %s \n } %s"
        
        limit_modifier = 'LIMIT 10'
        orderby_sparql = ''
        
        # add order by
        if modifier != None and modifier['orderby'] != None:
            orderby_sparql = ' ORDER BY '
            orderby = modifier['orderby']
            print 'orderby'
            print orderby
            
            for (spo, direction) in orderby:
                print spo
                print sparql_objects
                orderby_sparql += "%s( %s )" % (direction, sparql_objects[spo])
            
        query_modifiers = orderby_sparql + '\n' + limit_modifier
        return query_template % (query_prefixes, query_select_columns, query_body, query_modifiers), query_select_columns
        
    elif form=='ASK':
        query_template = "%s \n ASK WHERE { %s \n }"
        return query_template % (query_prefixes, query_body)
    else:
        print 'Wrong query form specified. Allowed: SELECT | ASK'
        return None


"""
returns the appropriate name for the subjects,predicates or objects in a sparql query
"""
def get_sparql_var_name(spo_element):
    # if is a predicate
    if isinstance(spo_element, PropertyDescriptor):
        return "%s:%s" % (spo_element.prop_prefix, spo_element.prop_name)
    # or wildcard predicate
    elif isinstance(spo_element, WildcardPredicate):
        return '?%s' % (spo_element.predicate_char)
    # is a reference (variable/Entity)
    else:
        # e.g. ?Actor1
        return "%s%d" % (spo_element.get_type(), spo_element.query_id)

def quote_string(string):
    return '\"%s\"' % string

"""
Question: list movies of 2016.
HARD-CODED. Returns the context generated by asking the question.
This should be job of the rasa_extractor
"""
def demo_listmovies_context():
    # first film entity present in the context (?film1)
    film_entity = Entity(film_entity_descriptor(), 1)

    # TODO: this is also declared identically in the film_entity_descriptor()
    # make a dictionary containing all the properties in Entity_Descriptor instead of a list? so you can do film_entitiy.props['name']
    name_property = PropertyDescriptor('Film', 'dbpprop', 'name', 'xsd', 'string')

    film_entity.add_spo(name_property, None)

    # Filters
    # Filter year on movie
    release_property = PropertyDescriptor('Film', 'ns', 'release', '', 'Release')
    # first Release entity of the context (?release1)
    release_entity = Entity(release_entity_descriptor(), 1)

    # releationship film_to_release
    film_entity.add_spo(release_property, release_entity)

    # filter on release's releaseDate property
    year_2016 = LiteralObject("2016")
    release_date_property = PropertyDescriptor('Release', 'dbpprop', 'year', 'xsd', 'string')
    release_entity.add_spo(release_date_property, year_2016)

    context = Context(all_entities=[film_entity, release_entity])

    return context

def demo_plot_of_film_context(movie_name_literal_object):
    # first film entity present in the context (?film1)
    film_entity = Entity(film_entity_descriptor(), 1)

    # TODO: this is also declared identically in the film_entity_descriptor()
    #       Solution: make a dictionary containing all the properties in Entity_Descriptor instead of a list? so you can do film_entitiy.props['name']
    name_property = PropertyDescriptor('Film', 'dbpprop', 'name', 'xsd', 'string')
    plot_property = PropertyDescriptor('Film', 'dbpprop', 'plot', 'xsd', 'string')

    # target: object is None, that means it is the target
    film_entity.add_spo(plot_property, None)

    # Filters
    # Filter name on movie
    film_entity.add_spo(name_property, movie_name_literal_object)

    context = Context(all_entities=[film_entity])

    return context
