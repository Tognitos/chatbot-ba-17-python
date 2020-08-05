from flask import Flask, redirect, session, jsonify, request, render_template, url_for
from backend.botcontroller import BotController
import yaml
import random
import logging
import sys

app = Flask(__name__, static_folder='frontend', static_url_path='')

# logging
logger = logging.getLogger("quepy")
logger.setLevel(logging.DEBUG)
myhandler = logging.FileHandler('debug.log')
myhandler.setLevel(logging.DEBUG)
myformatter = logging.Formatter(fmt='%(levelname)s: %(message)s')
myhandler.setFormatter(myformatter)
logger.addHandler(myhandler)

config = None
with open('config.yaml', 'r') as stream:
    try:
        config = yaml.load(stream)
        print('Configurations loaded:\n%s' % config)
    except yaml.YAMLError as exc:
        print(exc)

bot_controller = BotController(config)

@app.route('/')
def home():
    if 'sessionId' not in session:
        session['sessionId'] = random.randint(0,10000)
    return app.send_static_file('index.html')

@app.route('/logout')
def logout():
    session.pop('sessionId')
    return redirect('/')


@app.route('/query')
def query():
    if 'sessionId' not in session:
        return 'You are not logged in. Go to the homepage to get an ID'

    question = request.args.get('question').strip()
    message_answer, optional = bot_controller.query(question, session['sessionId'])

    result = None
    if optional == None:
        result = jsonify({'answer': message_answer.serialize()})
    else:
        result = jsonify({'answer': message_answer.serialize(),
                          'optional': optional.serialize()})

    return result



def main():
    app.secret_key = config['secret_key']
    app.run(debug=True)

if __name__ == '__main__':
    main()
