from flask import Flask, redirect, session, jsonify, request, render_template, url_for
from context import Context, Entity, EntityDescriptor, PropertyDescriptor, SPO, LiteralObject
from graph_metadata import *
from rasa_extractor import extract_from_text
from sparql_generator import execute_intent, generate_sparql_from_context

intent = None

# contains all past contexts
# old_contexts = []

def main():
    #"""
    print('scripted_flow')
    scripted_flow()
    #"""
    
    #"""
    print('example1_flow')
    example1_flow()
    #"""
    
    #"""
    print('example2_flow')
    example2_flow()
    #"""

     
"""
Example 1: (a) Add a filter to the old list
"""
def example1_flow():

    ## PART (I)
    question = 'List movies of 2016'
    print('Q:' + question)
    session_id = 1
    last_context = None
    
    intent, intent_confidence, entities, properties, literal_objects = extract_from_text(question)
    
    # now entities have all a sparql id
    # TODO: will conflict with entities of old context. We should not care about it in the beginning
    #entities = descriptor_to_entity(entities)
    
    # match each prop (predicate) to the most similar that can be found in our graph
    # e.g. 'acting' should become the spo_descriptor referring to 'dbpprop:starring'
    properties = predicate_to_descriptor(properties)
    
    # in this case is true
    threshold = 0.5
    if intent != None and intent_confidence > threshold :
        """
        context has to be built anyway, even if we know the intent, because we need it for further requests.
        context could be built by the intent manually, since we know already the entities and 
         predicates involved and do not have to deduce them from the question (i.e. we do not have to
         find good predicates for the literals or entities in the sentence).
        """
        results, context = execute_intent(intent, entities, properties, literal_objects)
        attachments = build_message_attachments(results)
        
        last_context = context
        
        # TODO:here we should return the answer based on the results ...
        
    else:
        pass
        # not going to happen for this question since we have a clear intent
        
        
    ## PART (II)
    question = 'only the ones with Tom Cruise'
    print('Q:' + question)
    session_id = 1
    
    intent, intent_confidence, entities, properties, literal_objects = extract_from_text(question)
    
    # now entities have all a sparql id
    # TODO: will conflict with same type of entities of old context. We should not care about it in the beginning
    #entities = descriptor_to_entity(entities)
    
    # match each prop (predicate) to the most similar that can be found in our graph
    # e.g. 'acting' should become the spo_descriptor referring to 'dbpprop:starring'
    properties = predicate_to_descriptor(properties)
    
    
    # this is not happening for this question
    if intent != None and intent_confidence > threshold :
        # printing if something goes wrong
        print('Intent should be None in part (II)')
        
    # intent is indeed not clear
    else:
        # we have it from Part (I)
        last_context = last_context
        
        # let's first generate a sort of 'local context' for the question itself. 
        # This is done because entities, literals and predicates first associate with each other in the same question 
        # All 3 variables change inside this method, that's why we re-assign them
        entities, properties, literal_objects = connect_subject_predicate_literal(entities, properties, literal_objects, 0.8)

        # find the right entity for the remaining properties and literals, if the entity isn't specified in the question
        additional_entities, properties, literal_objects = find_entity_for_predicate_literal(properties, literal_objects)
        entities += additional_entities
        
        # in this phase the Director entity should be associated with the Movie entity through the dbpprop:director predicate
        new_context = build_query_context(last_context, entities, properties, literal_objects)
        
        print('actor context as sparql')
        sparql = generate_sparql_from_context(new_context)
        print(sparql)
        
        last_context = new_context
        
        #TODO: here we should return the answer based on the results ...
        # ...
        
        
"""
Example 2: (a) Extract a property from the old context and (b) find the right intention (target) with the right data
"""
def example2_flow():

    ## PART (I)
    question = 'What is Titanic about?'
    print('Q:' + question)
    session_id = 1
    last_context = None
    
    intent, intent_confidence, entities, properties, literal_objects = extract_from_text(question)
    
    # now entities have all a sparql id
    # TODO: will conflict with entities of old context. We should not care about it in the beginning
    #entities = descriptor_to_entity(entities)
    
    # match each prop (predicate) to the most similar that can be found in our graph
    # e.g. 'acting' should become the spo_descriptor referring to 'dbpprop:starring'
    properties = predicate_to_descriptor(properties)
    
    # in this case is true
    threshold = 0.5
    if intent != None and intent_confidence > threshold :
        """
        context has to be built anyway, even if we know the intent, because we need it for further requests.
        context could be built by the intent manually, since we know already the entities and 
         predicates involved and do not have to deduce them from the question (i.e. we do not have to
         find good predicates for the literals or entities in the sentence).
        """
        results, context = execute_intent(intent, entities, properties, literal_objects)
        attachments = build_message_attachments(results)
        
        last_context = context
        
        # TODO:here we should return the answer based on the results ...
        
    else:
        pass
        # not going to happen for this question since we have a clear intent
        
        
    ## PART (II)
    question = 'who is the director?'
    print('Q:' + question)
    session_id = 1
    
    intent, intent_confidence, entities, properties, literal_objects = extract_from_text(question)
    
    # now entities have all a sparql id
    # TODO: will conflict with same type of entities of old context. We should not care about it in the beginning
    #entities = descriptor_to_entity(entities)
    
    # match each prop (predicate) to the most similar that can be found in our graph
    # e.g. 'acting' should become the spo_descriptor referring to 'dbpprop:starring'
    properties = predicate_to_descriptor(properties)
    
    
    # this is not happening for this question
    if intent != None and intent_confidence > threshold :
        # printing if something goes wrong
        print('Intent should be None in part (II)')
        
    # intent is indeed not clear
    else:
        # we have it from Part (I)
        last_context = last_context
        
        # let's first generate a sort of 'local context' for the question itself. 
        # This is done because entities, literals and predicates first associate with each other in the same question 
        # All 3 variables change inside this method, that's why we re-assign them
        entities, properties, literal_objects = connect_subject_predicate_literal(entities, properties, literal_objects, 0.8)

        # find the right entity for the remaining properties and literals, if the entity isn't specified in the question
        additional_entities, properties, literal_objects = find_entity_for_predicate_literal(properties, literal_objects)
        entities += additional_entities
        
        # in this phase the Director entity should be associated with the Movie entity through the dbpprop:director predicate
        new_context = build_query_context(last_context, entities, properties, literal_objects)
        
        print('actor context as sparql')
        print(new_context)
        sparql = generate_sparql_from_context(new_context)

        print(sparql)
        
        last_context = new_context
        
        #TODO: here we should return the answer based on the results ...
        # ...
       
              
        
"""
A simulation of context
"""
def scripted_flow():

    ## PART (I)
    question = 'List movies of 2016'
    print('Q:' + question)
    session_id = 1
    last_context = None
    
    intent, intent_confidence, entities, properties, literal_objects = extract_from_text(question)
    
    # now entities have all a sparql id
    # TODO: will conflict with entities of old context. We should not care about it in the beginning
    #entities = descriptor_to_entity(entities)
    
    # match each prop (predicate) to the most similar that can be found in our graph
    # e.g. 'acting' should become the spo_descriptor referring to 'dbpprop:starring'
    properties = predicate_to_descriptor(properties)
    
    # in this case is true
    threshold = 0.5
    if intent != None and intent_confidence > threshold :
        """
        context has to be built anyway, even if we know the intent, because we need it for further requests.
        context could be built by the intent manually, since we know already the entities and 
         predicates involved and do not have to deduce them from the question (i.e. we do not have to
         find good predicates for the literals or entities in the sentence).
        """
        results, context = execute_intent(intent, entities, properties, literal_objects)
        attachments = build_message_attachments(results)
        
        last_context = context
        
        # TODO:here we should return the answer based on the results ...
        
    else:
        pass
        # not going to happen for this question since we have a clear intent
        
        
    ## PART (II)
    question = 'Show me their directors'
    print('Q:' + question)
    session_id = 1
    
    intent, intent_confidence, entities, properties, literal_objects = extract_from_text(question)
    
    # now entities have all a sparql id
    # TODO: will conflict with same type of entities of old context. We should not care about it in the beginning
    #entities = descriptor_to_entity(entities)
    
    # match each prop (predicate) to the most similar that can be found in our graph
    # e.g. 'acting' should become the spo_descriptor referring to 'dbpprop:starring'
    properties = predicate_to_descriptor(properties)
    
    
    # this is not happening for this question
    if intent != None and intent_confidence > threshold :
        
        # printing if something goes wrong
        print('Intent should be None in part (II)')
    # intent is indeed not clear
    else:
        # we have it from Part (I)
        last_context = last_context
        
        # let's first generate a sort of 'local context' for the question itself. 
        # This is done because entities, literals and predicates first associate with each other in the same question 
        # All 3 variables change inside this method, that's why we re-assign them
        entities, properties, literal_objects = connect_subject_predicate_literal(entities, properties, literal_objects, 0.8)
        
        
        # in this phase the Director entity should be associated with the Movie entity through the dbpprop:director predicate
        new_context = build_query_context(last_context, entities, properties, literal_objects)
        
        print('director context as sparql')
        sparql = generate_sparql_from_context(new_context)
        print(sparql)
        
        last_context = new_context
        
        #TODO: here we should return the answer based on the results ...
        # ...
    

# builds the message attachments (answers) to be sent to the user
def build_message_attachments(results):
    return None

# gets the last context object based on the session id
def get_last_context(session_id):
    # TODO: use session id to determine last context
    n_contexts = len(old_contexts)
    if n_contexts > 0:
        return old_contexts[n_contexts]
    return None
    
        
"""
builds the new context structure (connects old entities with new ones, adds filters, determines predicates)
returns the generated context
"""
def build_query_context(last_context, entities, properties, literal_objects):
    if last_context == None:
        # TODO: should also try to match whatever it can (something better than nothing). 
        #           connect_subject_predicate_literal tries to be very sure and precise, so is not the best option here
        entities, properties, unassigned_literals = connect_subject_predicate_literal(entities, properties, literal_objects)
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
            predicate, confidence, should_reverse = get_best_fitting_predicate(old_entity, new_entity)

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

"""
Connects given entities, predicates and literal objects by finding a high match between a combination of the 3 of them.
This is be useful for generating the initial 'question context'
returns the resulting relationships (spo) and the remaining (unassigned) entities, properties and literals
"""
def connect_subject_predicate_literal(entities, properties, literal_objects, acceptance_threshold = 0.8):
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



"""
<property> = the name of the property returned by the extractor e.g. 'foaf:name'
<value> = the value of the object returned by the extractor e.g. 'Brad'

Select ?s Where {
    ?s <property1> <value1>.
    ?s <property2> <value2>.
    ?s ... ...
}
"""
# TODO: this work should be done on the SPARQL server as described in the comment above:
def find_entity_for_predicate_literal(properties, literal_objects):
    # look for entities in all graph
    entities_list = descriptor_to_entity(graph())
    entities, unassigned_properties, unassigned_literals = connect_subject_predicate_literal(entities_list, \
                                                               properties, literal_objects, acceptance_threshold = 0.8)
                                                               
    assigned_entities = list()
    for entity in entities:
        if len(entity.spos) > 0:
            # has been assigned
            assigned_entities.append(entity)
                                                                 
    return assigned_entities, unassigned_properties, unassigned_literals

"""
Looks for the predicate which fits best between 2 entities

returns 
    prop_name, 
    confidence
    reverse (bool): True is the relationship is from new_entity pointing to old_entity, False otherwise
"""

#TODO: now just the direct predicates are verified (and if domain and range match then it gets confidence=1)...
#       ...If the PropertyDescriptor prop_domain and prop_range would have references instead of strings defining the types, 
#       the connections could be navigated and the confidence could drop with a exponential rate (e.g. log(confidence, depth) or 1/exp(depth))
def get_best_fitting_predicate(old_entity, new_entity):
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
    
"""
Looks for the most similar predicate (based on word similarity, synonyms, ...)
returns the PropertyDescriptor corresponding to the most similar predicate
"""
# TODO: look for most similar predicate and return the corresponding PropertyDescriptors
def get_best_matching_predicate(predicate_text):
    return predicate_text
    # return best_matching_property_descriptor
    
"""
Helper method to convert from entity_descriptors (returned by the extractor) to queryable entities
"""
def descriptor_to_entity(entities):
    return [Entity(entity_descriptor, 1) for entity_descriptor in entities]

"""
Helper method to convert from properties as strings (returned by the extractor) to property descriptors
""" 
def predicate_to_descriptor(properties):
    return [get_best_matching_predicate(prop) for prop in properties]

# clears the useless elements from the context object, based on the should_clear policy
# returns the updated context without useless elements
def clear_context_items(last_context, new_context):
    pass
    
# returns true if the item should be removed from the context definetively
def should_clear_item(item):
    pass
    
    
        
if __name__ == '__main__':
    main()
