from pymongo import MongoClient, DESCENDING, errors
import cPickle as pickle

class History(object):

    def __init__(self, hostname, port, db, collection):
        self.client = MongoClient(hostname, port,serverSelectionTimeoutMS=2000)
        self.db = self.client[db]
        self.messages = self.db[collection]

        try:
            self.client.server_info()
            self.alive = True
        except errors.ServerSelectionTimeoutError as err:
            self.alive = False

    def keep(self, message):
        if not self.alive:
            return -1
        inserted_id = self.messages.insert_one(message.serialize()).inserted_id
        self.messages._id = inserted_id
        return inserted_id

    def update_feedback(self, session_id, percentage, expected_type):
        if not self.alive:
            return -1
        self.messages.find_one_and_update(
            {'sessionId': session_id, 'actor': 'bot'},
            {'$set': {'extra.satisfaction': percentage,
                      'extra.expectedType': expected_type}},
            sort=[('_id', DESCENDING)]
        )
        
    def query_message(self, session_id):
        if not self.alive:
            return None
        
        # find last message of that sessionId
        # WARNING: CANNOT use find_one because of the sort that would take place on the extracted record list
        cursor = self.messages.find({'sessionId': session_id, 'actor': 'bot'}).sort([('timestamp',-1)]).limit(1)
        try:
            record = cursor.next()
            return record
        except StopIteration:
            print("Empty cursor!")

        
        return None
        
    def get_last_context(self, session_id):
        last_message = self.query_message(session_id)

        if last_message == None or last_message['extra'] == None or last_message['extra']['context'] == None:
            return None
        
        context_dump = last_message['extra']['context']
        context_object = pickle.loads(str(context_dump))

        return context_object
