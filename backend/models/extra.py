
class Extra(object):

    def __init__(self, **kwargs):
        prop_defaults = {
            'satisfaction':   -1,
            'expected_type':  None,
            'creator':        None,
            'classification': None,
            'parameters':     [],
            'time_required':  0,
            'query':          '',
            'context':        None
        }

        for (prop, default) in prop_defaults.iteritems():
            setattr(self, prop, kwargs.get(prop, default))


    def serialize(self):
        return {
            'satisfaction':   self.satisfaction,
            'expectedType':   self.expected_type,
            'creator':        self.creator,
            'classification': self.classification,
            'parameters':     self.parameters,
            'timeRequired':   self.time_required,
            'query':          self.query,
            'context':        self.context
        }
