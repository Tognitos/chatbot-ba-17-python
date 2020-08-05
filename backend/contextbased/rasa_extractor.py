from graph_metadata import *
from context import *
from rasa_connector import RasaConnector
import default_intents as di
import simplejson as json # use simplejson because json doesn't work

class RasaExtractor(object):

    def __init__(self, url, history):
        self.rasa = RasaConnector(url)
        self._init_validation()

    def _init_validation(self):
        """Create a dictionary with the intent as the key and a list of entity
        types as value
        """
        self.required_type = {}
        with open('rasa_nlu/models/moviebot.json','r') as json_data:
            data = json.load(json_data)

        for example in data['rasa_nlu_data']['common_examples']:
            if example['intent'] in self.required_type:
                continue
            self.required_type[example['intent']] = map(\
                    lambda entity: entity['entity'], \
                    example['entities'])

    """
    calls the rasa extractor with the given human-written question text
    returns
        -intent
        -intent_confidence
        -entities
        -unassigned properties (predicates)
        -unassigned literals
    """
    def extract_from_text(self, question, old_context):
        result = self.rasa.query(question)

        self._validate(result)

        intent = result['intent']['name']
        intent_confidence = result['intent']['confidence']

        print 'Intent: %s' % intent
        print 'Intent confidence %f' % intent_confidence

        entities = []
        unassigned_properties = []
        unassigned_literals = []
        ranges = []
        confidence_threshold = 0.2
        modifier = None

        result_entities = result['entities']
        print 'Result entities: %s' % result_entities
        if len(result_entities) == 0:
            print('No entities could be extracted! Backup plan: Use POS Tags to extract "anything"?')
        elif intent != None and intent_confidence > confidence_threshold:
            entities, modifier = di.entities_for_intent(intent, result_entities, old_context)
            print(entities)
        else:
            # try to parse the entities and properties from the question
            entities, unassigned_properties, unassigned_literals, ranges = \
                self.parse_result_entities(result_entities)


        return intent, intent_confidence, entities, unassigned_properties, unassigned_literals, ranges, modifier

    def _validate(self, result):
        """Update the confidence result by comparing the extracted entity types
        with the required ones
        """
        entities_type = map(lambda entity: entity['entity'], result['entities'])
        intent_name = result['intent']['name']
        if len(entities_type) != len(self.required_type[intent_name]) or\
           not all(entity_type in self.required_type[intent_name] for entity_type in entities_type):
           result['intent']['confidence'] = 0

    @staticmethod
    def parse_result_entities(result_entities):
        """
        Parses the entities from the json result object returned by rasa.
        Returns
            - entities: Entity elements (e.g. 'Titanic')
            - unassigned_properties: predicates (e.g. 'Director', ...) which have not been assigned to an entity
            - unassigned_literals: literals (e.g. '2016', 'Tom', ...) which have not been assigned to an entity
            - ranges: list containing the range of indexes of each parsed entity [start,end, start, end, ...]
        """
        # gets info on the dataset
        graph_metadata = graph()

        entities = []
        unassigned_properties = [] # useless at the moment, since predicates are not extracted at all
        unassigned_literals = []
        ranges = []
        
        for result_entity in result_entities:
            entity_name = result_entity['entity']
            entity_value = result_entity['value']
            descriptor = RasaExtractor.find_descriptor_for_name(entity_name, graph_metadata)
            
            entity_start = result_entity['start']
            entity_end = result_entity['end']
            ranges.append(entity_start)
            ranges.append(entity_end)
            
            if descriptor == None:
                # no descriptor found for the specified name
                print('No descriptor found for entity %s with value %s' % (entity_name, entity_value))

                unassigned_literals.append(LiteralObject(entity_value))
            else:
                if isinstance(descriptor, EntityDescriptor):
                    # create entity instance
                    entity = Entity(descriptor, 1)

                    entity = RasaExtractor.associate_entity_with_identifying_value(entity, entity_value)

                    entities.append(entity)
                elif isinstance(descriptor, PropertyDescriptor):
                    # create entity instance from the Domain of the property
                    print('found prop')
                    # TODO: if the property would save a reference to the entity_descriptor, we wouldn't need to do the search again
                    entity_descriptor = RasaExtractor.find_descriptor_for_name(descriptor.prop_domain, graph_metadata)

                    literal_object = LiteralObject(entity_value)
                    existed = False

                    # check if the property can be attached to an entity that was created in this sentence without creating a new one
                    for created_entity in entities:
                        if entity_descriptor.type == created_entity.entity_descriptor.type:
                            existed = True
                            # add property to existing entity
                            created_entity.add_spo(descriptor, literal_object)
                            break

                    if existed == False:
                        entity = Entity(entity_descriptor, 1)
                        entity.add_spo(descriptor, literal_object)
                        entities.append(entity)

        return entities, unassigned_properties, unassigned_literals, ranges

    @staticmethod
    def find_descriptor_for_name(name, graph):
        """
        Finds the appropriate descriptor (entity or property) for the given name.
        It can be the name of an entity or a property.
        e.g. "dbpediaowl:Film", "dbpprop:director", ...
        """
        for entity_descriptor in graph:
            # if the name given matches to an entity return it
            if entity_descriptor.get_type() == name or entity_descriptor.get_rdftype() == name or ('%s:%s'%(entity_descriptor.get_type(), entity_descriptor.get_rdftype()) == name):
                return entity_descriptor
            else:
                for prop in entity_descriptor.properties:
                    if '%s:%s' % (prop.prop_prefix, prop.prop_name) == name or prop.prop_name == name:
                        print('prop:')
                        print(prop)
                        return prop

        # No descriptor found in whole Graph
        return None

    #TODO: do not just take the first one
    @staticmethod
    def associate_entity_with_identifying_value(entity, entity_value):
        """
        Finds the best predicate out of the default ones of the specified entity for the specified value.
        e.g. 'Titanic' should match to the Movie title, because that's what the value usually defines/identifies the movie
        """
        for predicate in entity.entity_descriptor.default_properties:
            if True:
                # we just take the first default predicate now for simplicity
                entity.add_spo(predicate, LiteralObject(entity_value))
                return entity
