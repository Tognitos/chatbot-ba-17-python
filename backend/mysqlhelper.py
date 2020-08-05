
import MySQLdb
import sys

def execute_sql(cursor, queries):
    print('Executing queries: %s' % queries)
    response=[]


    if type(queries) != type(list()):
        queries = [queries,]

    try:
        for query in queries:
            print('current query: %s' % query)
            if query.find("limit")==-1:
                query = query[:-1] + " limit 20;"
            result = cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                response.append(row[0].decode('iso-8859-1').encode('utf8'))
    except MySQLdb.Error as e:
            print("error", sys.exc_info()[0],e)
    except:
            print("error", sys.exc_info()[0])
    return response
