# chatbot-source

Setup the virtual environment
```
pip install virtualenv

virtualenv -p /usr/local/bin/python2.7 venv
```
OR
```
virtualenv -p /usr/bin/python2.7 venv
```
Finally activate it
```
source venv/bin/activate
```

Install the requirements
```
pip install -r requirements.txt
```

Copy the configuration file example and edit the new file
```
cp config.yaml.example config.yaml
```
Run the server
```
python server.py
```

## Check out the wiki for more information
https://github.com/panigsan/chatbot-source/wiki
