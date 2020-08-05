import apiai

class ApiAiHelper(object):

    def __init__(self, api_key):
        self.ai = apiai.ApiAI(api_key)
        self.count = 0


    def query(self, message, session_id, history_object):
        request = self.ai.text_request()

        request.session_id = self.count
        request.query = message

        response = request.getresponse()

        self.count += 1

        return response.read()
