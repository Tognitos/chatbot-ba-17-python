import requests
class RasaConnector(object):
    def __init__(self, url = 'http://localhost:5050/'):
        self.url = url

    def query(self, text):
        r = requests.get(self.url + 'parse?q=' + text)
        return r.json()
