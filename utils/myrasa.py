import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.contextbased.rasa_connector import RasaConnector

x = RasaConnector(url='http://localhost:5050/')

while True:
    question = raw_input()
    answer = x.query(question)
    print(json.dumps(answer,sort_keys=True,indent=2))
