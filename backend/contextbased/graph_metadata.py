from context import EntityDescriptor, PropertyDescriptor



# TODO: build graph with references instead of passing strings for prop_domain and prop_range
def graph():
    entity_descriptors = list()
    entity_descriptors.append(film_entity_descriptor())
    entity_descriptors.append(actor_entity_descriptor())
    entity_descriptors.append(director_entity_descriptor())
    entity_descriptors.append(release_entity_descriptor())
    return entity_descriptors

"""

should be "static"
"""
def film_entity_descriptor():
    name_property = PropertyDescriptor('Film', 'dbpprop', 'name', 'xsd', 'string')
    starring_property = PropertyDescriptor('Film', 'dbpprop', 'starring', '', 'Actor')
    director_property = PropertyDescriptor('Film', 'dbpprop', 'director', '', 'MovieDirector')
    release_property = PropertyDescriptor('Film', 'ns', 'release', '', 'Release')
    plot_property = PropertyDescriptor('Film', 'dbpprop', 'plot', 'xsd', 'string')
    genre_property = PropertyDescriptor('Film', 'dbpprop', 'genre', 'xsd', 'string')
    counter_property = PropertyDescriptor('Film', 'dbpprop', 'counter', 'xsd', 'integer')
    entity_desc = EntityDescriptor('Film', [name_property, starring_property, director_property, plot_property, genre_property, counter_property], [name_property])

    return entity_desc


"""
should be "static"
"""
def director_entity_descriptor():
    firstname_property = PropertyDescriptor('MovieDirector', 'foaf', 'name', 'xsd', 'string')
    lastname_property = PropertyDescriptor('MovieDirector','foaf', 'familyName', 'xsd', 'string')
    entity_desc = EntityDescriptor('MovieDirector', [firstname_property, lastname_property], [firstname_property, lastname_property])

    return entity_desc

def actor_entity_descriptor():
    firstname_property = PropertyDescriptor('Actor', 'foaf', 'name', 'xsd', 'string')
    lastname_property = PropertyDescriptor('Actor','foaf', 'familyName', 'xsd', 'string')
    entity_desc = EntityDescriptor('Actor', [firstname_property, lastname_property], [firstname_property, lastname_property])

    return entity_desc


"""
should be "static"
"""
def release_entity_descriptor():
    release_date_property = PropertyDescriptor('Release', 'dbpprop', 'releaseDate', 'xsd', 'integer')
    release_location_property = PropertyDescriptor('Release', 'dbpprop', 'releaseLocation', 'xsd', 'string')
    entity_desc = EntityDescriptor('Release', [release_location_property, release_date_property], [release_location_property, release_date_property], 'ns:Release')

    return entity_desc
