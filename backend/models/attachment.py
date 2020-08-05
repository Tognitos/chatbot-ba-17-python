
class Attachment(object):

    def __init__(self, content_type, content):
        self.content_type = content_type
        self.content = content

    def serialize(self):
        return {
            'contentType': self.content_type,
            'content':     self.content
        }
