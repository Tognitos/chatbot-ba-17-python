import quepy
import mysqlhelper
import MySQLdb
from models import Attachment

class IMDB(object):

    def __init__(self, host, user, passwd, db):
        self.connection = MySQLdb.connect(host =   host,
                                          user =   user,
                                          passwd = passwd,
                                          db =     db)
        self.dbbase = quepy.install("imdb")
        self.cursor = self.connection.cursor()

    def query(self, question, session_id, history_object):
        target, query, metadata = self.dbbase.get_query(question)
        results = mysqlhelper.execute_sql(self.cursor, query)
        print('target: %s' % target)
        print(metadata)


        attachment = Attachment('text', results[0]) if len(results) == 1 else\
                     Attachment('list', results)

        return attachment, (target, query, metadata)
