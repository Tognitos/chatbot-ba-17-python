class Context(object):
    def __init__(self, all_entities=[]):

        """
        All entities including the target entities.
        """
        self.all_entities = all_entities


        """
        target entity to be extracted.
        Should correspond to one of the Subjects of the relationships (e.g. ?filmRef)
        """
        #self.target_entities = target_entities

        """
        properties of the target entity to be extracted (list of Objects).
        Should correspond to one or more of the Objects of the relationships
        """
        #self.target_properties = target_properties

        """
        SPO (subject-predicate-object) relationships.
        One relationship must be at least the type of the target_entity.
        """
        #self.relationships = relationships

    """
    Creates a clone of the context.
    Warning: It only diassociates lists. It does NOT disassociate entities! (entities modified in one list will be modified in the other)
    """
    @staticmethod
    def clone(context_object):
        list_copy = [x for x in context_object.all_entities]
        copy = Context(all_entities=list_copy)
        return copy

    def find_entity(self, entity_type):
        for entity in self.all_entities:
            if entity.get_type() == entity_type:
                return entity
        return None




"""
SPO stands for subject-predicate-object relationship.
"""
class SPO(object):
    def __init__(self, s, p, o):
        """
        The subject of the relationship
        """
        self.s = s

        """
        The predicate of the relationship
        """
        self.p = p

        """
        The object of the relationship
        """
        self.o = o




"""
Describes the entity. Which type it is, which properties it may have and the default properties in case
 it is the target of Context and no desired property is specified
"""
class EntityDescriptor(object):
    def __init__(self, Type, properties, default_properties, rdf_type=None):
        """
        e.g. Film, Actor, Director, Person, Company, ...
        """
        self.type = Type

        """
        The properties that this entity can have.
        e.g. Film has dbpprop:name->xsd:string, dbpprop:starring->dbpediaowl:Actor, ...
        """
        self.properties = properties

        """
        If this Entity is the target of a Context, these are the properties that by default,
         if nothing else is specified, will be used as target properties by the Context
        """
        self.default_properties = default_properties

        if rdf_type==None:
            self.rdf_type = "dbp-owl:%s" % self.type
        else:
            self.rdf_type = rdf_type


    def get_type(self):
        return self.type

    def get_rdftype(self):
        return self.rdf_type

"""
Represents the instance of an Entity with a given EntityDescriptor and id inside a sparql query.
This is the object used to associate elements inside the relationships attribute in the Context class.

This could be seen as a IRI subject or IRI object of a relationship
"""
class Entity(object):
    def __init__(self, entity_descriptor, query_id):
        self.entity_descriptor = entity_descriptor

        """
        Id of this Entity inside the relationships of the Context class.
        This is used to relate to other Entities through subjects, in case there are multiple Entities with the SAME
         Entity Descriptor
        """
        self.query_id = query_id

        self.spos = list()

    def get_type(self):
        return self.entity_descriptor.get_type()

    def get_rdftype(self):
        return self.entity_descriptor.get_rdftype()

    def add_spo(self, p, o):
        """
        Return newly-added or updated spo    
        """
        for spo in self.spos:
            if spo.p.equalss(p):
                spo.o = o
                return spo

        new_spo = SPO(self, p, o)
        self.spos.append(new_spo)
        
        return new_spo

    def count_spos(self):
        return len(self.spos)

"""
Describes the property (predicate) of an Entity.

Another design choice could have been to specify the EntityDescriptor as an attribute to this class,
 or to simply add the type of the Entity as an attribute, because a property with the same name could have
 different ranges when belonging to different entities.
"""
class PropertyDescriptor(object):
    def __init__(self, prop_domain, prop_prefix, prop_name, prop_range_prefix, prop_range):
        """
        Domain of the property, e.g. Actor, Film , Work, Agent, ...
        """
        self.prop_domain = prop_domain

        """
        Prefix of the property, e.g. dbpprop, ns, foaf, ...
        """
        self.prop_prefix = prop_prefix

        """
        Name of the property, e.g. name, familyName, starring,...
        """
        self.prop_name = prop_name

        """
        Prefix of the range of the prefix. Typically xsd or dbpediaowl
        """
        self.prop_range_prefix = prop_range_prefix

        """
        Range of the property. This corresponds to the self.type of an Entity or to string, integer, ...
        """
        self.prop_range = prop_range

    def equalss(self, other):
        return self.prop_domain == other.prop_domain and\
               self.prop_prefix == other.prop_prefix and\
               self.prop_name   == other.prop_name   and\
               self.prop_range_prefix == other.prop_range_prefix and\
               self.prop_range  == other.prop_range

"""
Represents an object literal
"""
class LiteralObject(object):
    def __init__(self, value, literal_type = 'string'):
        self.value = value
        # e.g. string, number, year ...
        self.literal_type = literal_type


"""
To make predicates like ?p1 ?p2 ,..
"""
class WildcardPredicate(object):
    def __init__(self):
        self.predicate_char = 'p'
