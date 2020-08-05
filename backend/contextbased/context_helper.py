# coding: utf-8
from models import Attachment
from SPARQLWrapper import SPARQLWrapper, JSON
from sparql_generator import generate_sparql_from_context
from rasa_extractor import RasaExtractor
from context import Context, Entity, LiteralObject, WildcardPredicate
from models import Attachment, Message, Extra
import graph_metadata as gm
import cPickle as pickle
import nltk

idk = Attachment('text', 'I do not know how to answer')
no_answer = Attachment('text', '')


class ContextHelper(object):

    def __init__(self, sparql_endpoint, rasa_endpoint, history):
        self.sparql = SPARQLWrapper(sparql_endpoint)
        self.rasa = RasaExtractor(rasa_endpoint, history)
        self.history = history

    def query(self, question, session_id):

        # get the context for the question
        context, modifier = self.context_for_question(question, session_id)


        message_answer = Message(session_id  = session_id,
                                 actor       = 'bot',
                                 terminated  = False)

        extra = Extra(creator = 'context_helper', context = pickle.dumps(context))
        message_answer.extra = extra

        if context.all_entities != None:
            # get query and selected columns names (those will be useful for the parsing)
            query, select_columns = generate_sparql_from_context(context, modifier=modifier)

            print(query)
            print ('select columns:')
            print(select_columns)

            # execute the sparql query and obtain results
            self.sparql.setQuery(query)
            self.sparql.setReturnFormat(JSON)

            results = self.sparql.query().convert()

            if not results["results"]["bindings"]:
                print ("No answer found :(")
                return message_answer

            bindings = results["results"]["bindings"]

            attachment = ContextHelper.parse_response(bindings, select_columns)

            message_answer.attachments = [attachment]
        else:
            message_answer.attachments = [idk]


        return message_answer

    @staticmethod
    def remove_ranges_from_string(text, ranges, confidence):
        """
        Remove all the words that have been matched in the text by the extractor
        """
        # must be higher than this, otherwise we cannot trust the entities
        threshold_confidence = 0.1
        if confidence < threshold_confidence:
            return text
        
        print 'dirty_text'
        print text
        print 'ranges'
        print ranges
        cleaned_text = ''
        i = 0
        last_pos = 0

        while i < len(ranges):
            el = ranges[i]

            if i % 2 == 0:
                cleaned_text += text[last_pos:el]
            else:
                last_pos = el
            i += 1
        cleaned_text += text[last_pos:len(text)]
        print 'cleaned_text'
        print cleaned_text

        return cleaned_text

    """
    Everything with context starts from this method
    """
    def context_for_question(self, question, session_id):
        last_context = self.history.get_last_context(session_id)
        
        intent, intent_confidence, entities, properties, literal_objects, ranges, modifiers = self.rasa.extract_from_text(question, last_context)

        # remove all the parts where an entity has been matched
        unmatched_text = ContextHelper.remove_ranges_from_string(question, ranges, intent_confidence)
        # use nltk to find all possible literals in the sentence
        possible_literals = self.get_literals_from_text(unmatched_text)
        # Uses the wildcard predicate to find the appropriate subject for each literal
        entities = self.find_subject_type_for_literals(entities, possible_literals)

        # match each prop (predicate) to the most similar that can be found in our graph
        # e.g. 'acting' should become the spo_descriptor referring to 'dbpprop:starring'

        # Useful just if the properties are not matched in the rasa extractor
        properties = ContextHelper.predicate_to_descriptor(properties)


        threshold = 0.2
        if intent != None and intent_confidence > threshold :
            print(intent_confidence)
            print(entities)
            # if intent is clear, the context is hard-coded
            context = Context(entities)

            return context, modifiers

        else:
            # let's first generate a sort of 'local context' for the question itself.
            # This is done because entities, literals and predicates first associate with each other in the same question
            # All 3 elements (subject, predicates and objects) must be present in the question in order to be matched together.
            # This way we avoid matching literals to entities of the same question when they belong to entities of previous contexts
            entities, properties, literal_objects = self.connect_subject_predicate_literal(entities, properties, literal_objects, 0.8)

            # find the right entity for the remaining properties and literals, if the entity isn't specified in the question
            additional_entities, properties, literal_objects = self.find_entity_for_predicate_literal(properties, literal_objects)
            entities += additional_entities

            # in this phase the Director entity should be associated with the Movie entity through the dbpprop:director predicate
            new_context = self.build_query_context(last_context, entities, properties, literal_objects)

            return new_context, modifiers


    def connect_subject_predicate_literal(self, entities, properties, literal_objects, acceptance_threshold = 0.8):
        """
        Connects given entities, predicates and literal objects by finding a high match between a combination of the 3 of them.
        This is be useful for generating the initial 'question context'
        returns the resulting relationships (spo) and the remaining (unassigned) entities, properties and literals
        """
        unassigned_literals = [lit for lit in literal_objects]

        # match the entities with the literal_objects based on the matched_properties
        # every literal that gets matched with a probability high enough gets removed from the list
        for literal in literal_objects:
            best_prop = None
            best_entity = None
            max_score = acceptance_threshold
            for prop in properties:
                for entity in entities:
                    # score is 50% common entity type, 50% same object type
                    # TODO: same domain may have properties with same range (e.g. Film follows Film, Film version of Film, ...)
                    # but different property name  --> Name is important as well!
                    score = 0.50 * int(entity.get_type() == prop.prop_domain) + 0.50 * int(literal.literal_type == prop.prop_range)
                    if score > max_score:
                        best_prop = prop
                        best_entity = entity
                        max_score = score

            if best_prop != None:
                best_entity.add_spo(best_prop, literal)
                properties.remove(best_prop)
                unassigned_literals.remove(literal)

        return entities, properties, unassigned_literals


    def build_query_context(self, last_context, entities, properties, literal_objects):
        """
        builds the new context structure (connects old entities with new ones, adds filters, determines predicates)
        returns the generated context
        """
        if last_context == None:
            # TODO: should also try to match whatever it can (something better than nothing).
            #           connect_subject_predicate_literal tries to be very sure and precise, so is not the best option here
            entities, properties, unassigned_literals = self.connect_subject_predicate_literal(entities, properties, literal_objects)
            return Context(all_entities=entities)

        # Cloned context contains a disassociate list, but the entities objects are still the same!
        # new_context = Context.clone(last_context)
        new_context = Context(all_entities=entities)

        # minimum confidence necessary to be accepted as valid predicate
        confidence_threshold = 0.3


        #new_context.all_entities += entities

        for new_entity in entities:
            # the max confidence of the highest rated (best_predicate, best_old_entity) tuple
            max_confidence = confidence_threshold

            # entity of the old context which relates the most with the new entity
            best_old_entity = None

            # predicate with which the best_old_entity relates to the new_entity
            best_predicate = None

            # True if relationship points from new_entity to old_entity
            should_reverse = False

            # if confidence is high enough (e.g. > 0.95) we don't look for more predicates so that we speed up the search
            sure_enough_confidence = 0.95


            # look for entities in the old context
            for old_entity in last_context.all_entities:
                # look for the best matching predicate. Gives the priority to predicates pointing from old to new instead of new->old
                # the subject and object must be inverted if the relationship is new pointing to old entity, instead of old pointing to new
                predicate, confidence, should_reverse = self.get_best_fitting_predicate(old_entity, new_entity)

                if confidence > max_confidence:
                    best_predicate = predicate
                    best_old_entity = old_entity
                    max_confidence = confidence

                # if we are sure enough we stop looking for connections between other old_entities
                if max_confidence > sure_enough_confidence:
                    break

            if best_predicate == None:
                print('no predicate found for ' + new_entity.get_type())
            else:
                # by default old points at new one
                if should_reverse == False:
                    best_old_entity.add_spo(best_predicate, new_entity)
                else:
                    new_entity.add_spo(best_predicate, best_old_entity)


        # at least every subject which is not filtered (i.e. has just the rdf:type SPO) is a target
        # as a consequence we also have to get the default properties for that target entity, since we do not want to extract its IRI
        for entity in new_context.all_entities:
            if entity.count_spos() == 0:
                for target_property in entity.entity_descriptor.default_properties:
                    # if object of a SPO is equal to None, then it means is not filtered, therefore the user wants to extract this information
                    entity.add_spo(target_property, None)

        """
        Remove any SPO of the old entities that was a target, unless the property is one of the defaults of the object!
        If the entity has no more SPOs then it means that it became useless and should not be added.
        If the entity has at least one SPO remaining then it means it has been connected to something of the new context

        e.g. Before we selected name and plot of some movies. After we ask for the director. Name of movie should stay because is part of default props.
               Plot must disappear because no new entity has been connected to the plot (assuming plot was an IRI and not a literal).

        TODO: problem when the relationship is reversed (look above, when should_reverse=True).
                Because then we maybe remove all SPOs of an old entity that has been successfully linked with a new entity!
        """
        for entity in last_context.all_entities:
            # Pseudo-code for what is missing here
            # if entity is_object_of any_new_entity:
            #   new_context.all_entities.append(entity)
            #   continue (skip the rest of the for-loop)
            # TODO: make an example of when this would happen (should_reverse == True), but yeah: when does should_reverse happen?
            # e.g. 'Show me the age of Brad Pitt' -- then --> 'Show movies starring him' ==> should_reverse = true

            for spo in entity.spos:
                if spo.o == None:
                    pass
                    #TODO: this partially works
                    #entity.spos.remove(spo)
            if len(entity.spos) > 0:
                new_context.all_entities.append(entity)
            else:
                # TODO: the entity with no more SPOs should be removed at all. However, have a look at the todo above this for-cycle
                pass
        return new_context


    # TODO: this work should be done on the SPARQL server as described in the comment above:
    def find_entity_for_predicate_literal(self, properties, literal_objects):
        """
        <property> = the name of the property returned by the extractor e.g. 'foaf:name'
        <value> = the value of the object returned by the extractor e.g. 'Brad'

        Select ?s Where {
            ?s <property1> <value1>.
            ?s <property2> <value2>.
            ?s ... ...
        }
        """
        # look for entities in all graph (from metadata)
        entities_list = ContextHelper.descriptor_to_entity(gm.graph())
        entities, unassigned_properties, unassigned_literals = self.connect_subject_predicate_literal(entities_list, \
                                                                   properties, literal_objects, acceptance_threshold = 0.8)

        assigned_entities = list()
        for entity in entities:
            if len(entity.spos) > 0:
                # has been assigned
                assigned_entities.append(entity)

        return assigned_entities, unassigned_properties, unassigned_literals

    #TODO: now just the direct predicates are verified (and if domain and range match then it gets confidence=1)...
    #       ...If the PropertyDescriptor prop_domain and prop_range would have references instead of strings defining the types,
    #       the connections could be navigated and the confidence could drop with a exponential rate (e.g. log(confidence, depth) or 1/exp(depth))
    def get_best_fitting_predicate(self, old_entity, new_entity):
        """Looks for the predicate which fits best between 2 entities

        returns
            prop_name,
            confidence
            reverse (bool): True is the relationship is from new_entity pointing to old_entity, False otherwise
        """
        old_descriptor = old_entity.entity_descriptor
        new_descriptor = new_entity.entity_descriptor

        # TODO: drop confidence (probably exponentially) as distance/depth between the 2 entities increases
        best_confidence = 0.0
        best_property = None
        reverse = False

        # check props from old->new (has the priority because that's usually how people write sentences I suppose)
        for old_prop in old_descriptor.properties:
            if old_prop.prop_range == new_descriptor.get_type():
                # TODO: make it depend on the depth (see todo above the function declaration)
                confidence = 1.0
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_property = old_prop
                    reverse = False

        # check props from new->old
        for new_prop in new_descriptor.properties:
            if new_prop.prop_range == old_descriptor.get_type():
                # TODO: make it depend on the depth (see todo above the function declaration)
                confidence = 1.0
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_property = new_prop
                    reverse = False

        return best_property, best_confidence, reverse


    # TODO: look for most similar predicate and return the corresponding PropertyDescriptors
    def get_best_matching_predicate(self, predicate_text):
        """ Looks for the most similar predicate (based on word similarity, synonyms, ...).
        returns the PropertyDescriptor corresponding to the most similar predicate
        """
        return predicate_text
        # return best_matching_property_descriptor


    def find_subject_type_for_literals(self, entities, literals):
        """
        Associates each literal to the entity with the entity type that would return a result if it had no filters except from the literal.

        Return:
        - (possibly) updated entities

        foreach literal
            foreach entity
                if ASK_QUERY with EntityType_WildcardPredicate_Literal has a solution then
                    entity.add_spo(WildcardPredicate, Literal)
                    break
                else
                    continue
        """

        wildcard_predicate = WildcardPredicate()
        for literal in literals:
            for entity in entities:
                # dereference from old entity
                clean_entity = Entity(entity.entity_descriptor, 1)
                clean_entity.add_spo(wildcard_predicate, literal)

                path_exists = self.ask_path_exists(Context([clean_entity]))

                if path_exists:
                    entity.add_spo(wildcard_predicate, literal)
                    break

        return entities

    def ask_path_exists(self, context):
        """
        Executes an ASK query on the SPARQL dataset. The answer is a boolean true or false.
        """
        # get query and selected columns names (those will be useful for the parsing)
        query = generate_sparql_from_context(context, form='ASK')

        print 'Asking something'
        #print(query)

        # execute the sparql query and obtain results
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)

        results = self.sparql.query().convert()

        #print results
        """
        if not results["results"]["bindings"]:
            print ("No answer found :(")
            return message_answer

        bindings = results["results"]["bindings"]

        attachment = ContextHelper.parse_response(bindings, select_columns)
        """
        return False



    def get_literals_from_text(self, text):
        """
        Tags found here
        http://stackoverflow.com/questions/15388831/what-are-all-possible-pos-tags-of-nltk
        """

        # use nltk to find all possible literals in the sentence
        literals = []

        string_tags = ['JJ', 'JJR', 'JJS', 'NN', 'NNP', 'NNS']
        numeric_tags = ['CD']

        tokens = nltk.word_tokenize(text)
        print 'tokens'
        print tokens


        tagged = nltk.pos_tag(tokens)

        print 'tagged'
        print tagged

        for (token, tag) in tagged:
            if tag in string_tags:
                literals.append(LiteralObject(token))
            elif tag in numeric_tags:
                literals.append(LiteralObject(token, 'numeric'))

        return literals
    """
    def get_literals_from_entities(self, entities):
        # return literals that are already associated to entities
        literals = []
        for entity in entities:
            for spo in entity.spos:
                if isinstance(spo.o, LiteralObject):
                    literals.append(spo.o)

        return literals
    """

    @staticmethod
    def predicate_to_descriptor(properties):
        """Helper method to convert from properties as strings (returned by the extractor) to property descriptors
        """
        return [get_best_matching_predicate(prop) for prop in properties]

    @staticmethod
    def descriptor_to_entity(entities):
        """
        Helper method to convert from entity_descriptors (returned by the extractor) to queryable entities
        """
        return [Entity(entity_descriptor, 1) for entity_descriptor in entities]


    @staticmethod
    def parse_response(bindings, select_columns):
        attachment_type = 'text' if len(bindings) == 1 else 'list'
        results = []
        # for every row
        for binding in bindings:
            line = []
            print('binding')
            print(binding)
            # for every column
            for k,v in binding.iteritems():
                if k in select_columns:
                    line.append(v['value'])
                    
            results.append(' '.join(line))

        return Attachment(attachment_type, results)
