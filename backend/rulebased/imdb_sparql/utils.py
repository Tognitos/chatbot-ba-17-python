
class MyExtra(object):
    def __init__(self, extra):
        self.extra = extra

class OrderBy(object):
    def __init__(self, text):
        self.text = "ORDER BY " + text

def replace_prop(element, relation, newvalue):
    for node in range(len(element.nodes)):
        for edge in range(len(element.nodes[node])):
            t_relation, value = element.nodes[node][edge]
            if relation == t_relation:
                element.nodes[node][edge] = (relation, newvalue)
                return value
