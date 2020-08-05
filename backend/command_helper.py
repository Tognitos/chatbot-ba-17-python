from models import Attachment, Message, Extra
class CommandHelper(object):

    def __init__(self):
        pass

    def query(self, message_question, session_id):

        message_answer = Message(session_id  = session_id,
                                 actor       = 'bot',
                                 terminated  = False)

        extra = Extra(creator = 'command') # command: starts with ':'

        # TODO: analyse the content_type first!
        question = message_question.attachments[0].content

        attachments = None
        if question == ':hello':
            attachments = [Attachment('question', 'Hi, how can I help you?'),
                           Attachment('text', 'Type <b>:help</b> for a list of commands')]
            extra.query = ':hello'

        elif question == ':help':
            attachments = [Attachment('text', 'You asked for help. I think I can ' \
                                    + 'help you: https://google.com'),
                           Attachment('list', [':hello',
                                               ':help',
                                               ':youtube',
                                               ':list',
                                               ':histogram',
                                               ':pie'])]
            extra.query = ':help'

        elif question == ':youtube':
            attachments = [Attachment('text', 'Here is the trailer of Inception (2010)'),
                           Attachment('youtube', 'https://www.youtube.com/embed/YoHD9XEInc0')]
            extra.query = ':youtube'

        elif question == ':list':
            attachments = [Attachment('text', 'Here is your list'),
                           Attachment('list', [1,2,3]),
                           Attachment('question', 'Do you need something else?')]
            extra.query = ':list'

        elif question == ':histogram':
            attachments = [Attachment('text', 'Here are some statistics'),
                       Attachment('histogram', {
                        'title' : '# votes',
                        'labels': ["Fast and Furios", "Casablanca",
                                   "Gran Torino", "Game of Thrones"],
                        'values': [12, 19, 3, 5]
                       }),
                       Attachment('question', 'Did you find this useful?')]
            extra.query = ':histogram'

        elif question == ':pie':
            attachments = [Attachment('text', 'Here is the appreciationrate in stars for Casablanca'),
                       Attachment('pie', {
                        'labels': ["1 Star", "2 Stars", "3 Stars", "4 Stars", "5 Stars"],
                        'values': [205, 1313, 5333, 12023, 33333]
                       }),
                       Attachment('question', 'Did you find this useful?')]
            extra.query = ':pie'

        else:
            return None

        message_answer.attachments = attachments
        message_answer.extra = extra

        return message_answer
