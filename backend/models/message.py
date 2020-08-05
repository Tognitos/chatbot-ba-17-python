from datetime import datetime

class Message(object):
    def __init__(self, **kwargs):
        prop_defaults = {
            'session_id':    0,
            'version':       '0.0.1',
            'timestamp':     datetime.now(),
            'lang':          'en',
            'actor':         None, # from
            'reset_context': False,
            'attachments':   [],
            'terminated':    False,
            'extra':         None
        }

        for (prop, default) in prop_defaults.iteritems():
            setattr(self, prop, kwargs.get(prop, default))

    def serialize(self, include_extra = True):
        return {
            'sessionId':    self.session_id,
            'version':      self.version,
            'timestamp':    self.timestamp,
            'lang':         self.lang,
            'actor':        self.actor,
            'resetContext': self.reset_context,
            'attachments':  [a.serialize() for a in self.attachments],
            'terminated':   self.terminated,
            'extra':        self.extra.serialize() \
                                if (self.extra != None and include_extra) \
                                else None
        }
