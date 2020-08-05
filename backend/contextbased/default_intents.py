from context import *
from graph_metadata import *

"""
Takes an intent and a list of result_entities ("json").
Returns a list of entities (Entity instances) from which the context will be constructed.
"""
def entities_for_intent(intent, result_entities, old_context):
    # call the function with the same name as the intent
    #print('Intent: %s' % intent)
    return globals()[intent](result_entities, old_context)


def addFilter(entity, prop_prefix, prop_name, value):
    for prop in entity.entity_descriptor.properties:
        if prop.prop_prefix == prop_prefix and prop.prop_name == prop_name:
            o = None
            if value != None:
                o = LiteralObject(value, prop.prop_range)

            return entity.add_spo(prop, o)

def budgetOf(result_entities, old_context = None):
    movie_entity = Entity(film_entity_descriptor(), 1)

    # add the filter on the name
    movie_name = result_entities[0]['value']
    addFilter(movie_entity, 'dbpprop', 'name', movie_name)

    # targets
    budget_property = PropertyDescriptor('Film', 'dbpprop', 'budget', '', 'string')
    movie_entity.add_spo(budget_property, None)
    
    modifier = None
    
    return [movie_entity], modifier


def durationOf(result_entities, old_context = None):
    movie_entity = Entity(film_entity_descriptor(), 1)

    # add the filter on the name
    movie_name = result_entities[0]['value']
    addFilter(movie_entity, 'dbpprop', 'name', movie_name)

    # targets
    duration_property = PropertyDescriptor('Film', 'dbpprop', 'filmRuntime', '', 'string')
    movie_entity.add_spo(duration_property, None)
    
    modifier = None
    
    return [movie_entity], modifier


def plotOf(result_entities, old_context = None):
    movie_entity = Entity(film_entity_descriptor(), 1)

    # add the filter on the name
    movie_name = result_entities[0]['value']
    addFilter(movie_entity, 'dbpprop', 'name', movie_name)

    # targets
    plot_property = PropertyDescriptor('Film', 'dbpprop', 'plot', '', 'string')
    movie_entity.add_spo(plot_property, None)

    modifier = None
    
    return [movie_entity], modifier


def moviesOfGenre(result_entities, old_context = None):
    movie_entity = None
    if old_context == None:
        movie_entity = Entity(film_entity_descriptor(), 1)
    else:
        movie_entity = old_context.find_entity('Film')
        if movie_entity == None:
            print 'Movie entity not found'
            return []

    # add the filter on the name
    genre_name = result_entities[0]['value']
    addFilter(movie_entity, 'dbpprop', 'genre', genre_name)
    
    counter_spo = addFilter(movie_entity, 'dbpprop', 'counter', None)

    # targets
    plot_property = PropertyDescriptor('Film', 'dbpprop', 'name', '', 'string')
    movie_entity.add_spo(plot_property, None)

    print 'counter spo'
    print counter_spo
    modifier = {'orderby' : [(counter_spo, 'DESC')]}
    
    if old_context == None:
        return [movie_entity], modifier
    else:
        return old_context.all_entities, modifier


def moviesOfDirector(result_entities, old_context = None):
    movie_entity = None
    if old_context == None:
        movie_entity = Entity(film_entity_descriptor(), 1)
    else:
        movie_entity = old_context.find_entity('Film')
        if movie_entity == None:
            print 'Movie entity not found'
            return []

    director_entity = Entity(director_entity_descriptor(), 1)

    # add the filter on the name
    director_name = next(x['value'] for x in result_entities if x['entity']=='foaf:name')
    director_familyname = next(x['value'] for x in result_entities if x['entity']=='foaf:familyName')

    addFilter(director_entity, 'foaf', 'name', director_name)
    addFilter(director_entity, 'foaf', 'familyName', director_familyname)

    # targets
    title_property = PropertyDescriptor('Film', 'dbpprop', 'name', '', 'string')
    movie_entity.add_spo(title_property, None)

    # links
    director_property = PropertyDescriptor('Film', 'dbpprop', 'director', '', 'string')
    movie_entity.add_spo(director_property, director_entity)

    modifier = None
    
    if old_context == None:
        return [movie_entity, director_entity], modifier
    else:
        return old_context.all_entities + [director_entity], modifier


def moviesOfYear(result_entities, old_context = None):
    movie_entity = Entity(film_entity_descriptor(), 1)
    release_entity = Entity(release_entity_descriptor(), 1)

    # add the filter on the release year
    release_year = next(x['value'] for x in result_entities if x['entity']=='dbpprop:releaseDate')

    addFilter(release_entity, 'dbpprop', 'releaseDate', release_year)
    # default release location USA (removes a lot of duplicates)
    addFilter(release_entity, 'dbpprop', 'releaseLocation', "USA")

    # targets
    title_property = PropertyDescriptor('Film', 'dbpprop', 'name', '', 'string')
    movie_entity.add_spo(title_property, None)

    # links
    release_property = PropertyDescriptor('Film', 'ns', 'release', 'ns', 'Release')
    movie_entity.add_spo(release_property, release_entity)

    modifier = None
    

    return [movie_entity, release_entity], modifier


def releaseDateOf(result_entities, old_context = None):
    movie_entity = Entity(film_entity_descriptor(), 1)
    release_entity = Entity(release_entity_descriptor(),1)

    # add the filter on the name
    movie_name = result_entities[0]['value']
    addFilter(movie_entity, 'dbpprop', 'name', movie_name)

    addFilter(release_entity, 'dbpprop', 'releaseLocation', 'USA')

    # targets
    release_property = PropertyDescriptor('Release', 'dbpprop', 'releaseDate', '', 'string')
    release_spo = release_entity.add_spo(release_property, None)

    # links
    release_property = PropertyDescriptor('Film', 'ns', 'release', 'ns', 'Release')
    movie_entity.add_spo(release_property, release_entity)
    
    modifier = None
    
    return [movie_entity, release_entity], modifier


def starringIn(result_entities, old_context = None):
    movie_entity = Entity(film_entity_descriptor(), 1)
    actor_entity = Entity(actor_entity_descriptor(), 1)

    # add the filter on the name
    movie_name = result_entities[0]['value']
    addFilter(movie_entity, 'dbpprop', 'name', movie_name)

    # targets
    person_name_property = PropertyDescriptor('Actor', 'foaf', 'name', '', 'string')
    person_lastname_property = PropertyDescriptor('Actor', 'foaf', 'familyName', '', 'string')
    
    actor_entity.add_spo(person_name_property, None)
    actor_entity.add_spo(person_lastname_property, None)
    
    # links
    starring_property = PropertyDescriptor('Film', 'dbpprop', 'starring', '', 'Actor')
    movie_entity.add_spo(starring_property, actor_entity)

    modifier = None
    
    return [movie_entity, actor_entity], modifier
