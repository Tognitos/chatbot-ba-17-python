from models import Attachment, Message, Extra
from rulebased.imdbhelper import IMDB
from rulebased.imdbhelper_sparql import IMDB_SPARQL
from online import ApiAiHelper
from datetime import datetime
from time import time
from command_helper import CommandHelper

# Context stuff
from contextbased.context_helper import ContextHelper

version = 'context_based'

class Bot(object):
    def __init__(self, config, history):
        self.command_helper = CommandHelper()
        
        if version == 'rulebased_sparql':
            self.imdb = IMDB_SPARQL(config['imdb_sparql']['url'])
            
        elif version == 'rulebased_sql':
            self.imdb = IMDB(host   = config['imdb']['host'],
                             user   = config['imdb']['user'],
                             passwd = config['imdb']['passwd'],
                             db     = config['imdb']['db'])
                             
        elif version == 'api_ai':
            self.apiai = ApiAiHelper(config['apiai']['dev_key'])
            
        elif version == 'context_based':
            # read from config
            sparql_endpoint = config['imdb_sparql']['url']
            rasa_endpoint = config['rasa']['url']
            
            # instantiate context helper
            self.imdb = ContextHelper(sparql_endpoint, rasa_endpoint, history)
            
        else:
            sys.exit('NO BOT VERSION SPECIFIED')
            


    def query(self, message_question, session_id):
        start_time = int(time()*(10**6)) # in microseconds

        message_answer = self.command_helper.query(message_question,session_id)

        if message_answer == None:
            question = message_question.attachments[0].content
            message_answer = self.imdb.query(question, session_id)


        elapsed = int(time()*(10**6)) - start_time
        message_answer.extra.time_required = elapsed

        return message_answer
