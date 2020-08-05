from bot import Bot
from history import History
from models import Attachment, Message
import re


class BotController(object):

    def __init__(self, config):
        self.history = History(config['logserver']['hostname'],
                               config['logserver']['port'],
                               config['logserver']['db'],
                               config['logserver']['collection'])
                               
        self.bot = Bot(config, self.history)


    def query(self, question, session_id):

        # try to handle a feedback, it may return the user message with
        # content_type 'feedback' and a thankful message from the controller
        user_message, controller_message = self.handle_feedback(question, session_id)
        if user_message != None and controller_message != None:
            self.history.keep(user_message)
            self.history.keep(controller_message)
            return controller_message, None


        message_attachment = Attachment(content_type = 'text',
                                        content      = question)
        message_question = Message(session_id  = session_id,
                                   actor       = 'user',
                                   attachments = [message_attachment])

        self.history.keep(message_question)

        # TODO: routing
        message_answer = self.bot.query(message_question, session_id)

        self.history.keep(message_answer)


        optional = None
        # if the bot cannot answer anymore, the flag terminated is set True,
        # the service will ask for a feedback
        if message_answer.terminated:
            optional = Message(
                session_id  = session_id,
                actor       = 'controller',
                attachments = [Attachment(content_type = 'feedback',
                    content = 'Did you get what you expected? ' + \
                              'Please write something like<br> ' + \
                              '<i>:feedback &lt;percentage&gt; ' + \
                              '&lt;list|trailer|other expected type&gt;</i><br>' +\
                              'Example: <i>:feedback 100 list</i>')])
            self.history.keep(optional)

        return message_answer, optional

    def handle_feedback(self, question, session_id):
        # a feedback has to follow this reg ex, examples:
        # valid: ':feedback 0 list', ':feedback 10 youtube', ':feedback 100 list'
        # not valid: ':feedback a', ':feedback 1000 list trailer'
        m = re.match(':feedback (\d{1,3}) (\w+)$', question)

        if m == None:
            return None, None

        percentage = m.group(1)
        expected_type = m.group(2)

        self.history.update_feedback(session_id, percentage, expected_type)

        controller_message = Message(
            session_id  = session_id,
            actor       = 'controller',
            attachments = [Attachment(content_type = 'text',
                            content = 'Thank you for the feedback')])

        user_message = Message(
            session_id = session_id,
            actor      = 'user',
            attachments = [Attachment(content_type = 'feedback',
                            content = {'percentage':   percentage,
                                       'expectedType': expected_type})])


        return user_message, controller_message
