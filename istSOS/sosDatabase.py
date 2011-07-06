import psycopg2 # @TODO the right library
import psycopg2.extras

class Database:
    "Connect to a database"
    user = None
    password = None
    host = None
    dbName = None
    port = None
    def getConnection(self):
        "Return a database connection"
        return None;
    def closeConnection(self):
        "close a database connection"
        return None

class sosPgDB(Database):
    "Connect to a PostgreSQL database"
    host=None
    def __init__(self,user,password,dbName,host='localhost',port='5432'):
        "Initialize PostgreSQL connection parameters"
        self.__dns=""
        if host: self.__dns += "host='%s' " % host
        if port: self.__dns += "port='%d' " % int(port)
        if dbName: self.__dns += "dbname='%s' " % dbName
        if user: self.__dns += "user='%s' " % user
        if password: self.__dns += "password='%s' " % password
        self.__connect()
    
    def __connect(self):
        "Connect to a PostgreSQL database"
        try:
            self.__conn=psycopg2.connect(self.__dns)
        except psycopg2.ProgrammingError, e:
            print e.message
            
    def select(self,sql):
        if sql.lstrip()[0:6].lower() == "select":
            cur = self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            try:
                cur.execute(sql)
            except psycopg2.ProgrammingError as e:
                print e.message
            try:
                rows = cur.fetchall()
            except:
                rows = None
            #self.__conn.commit()
            cur.close()
            return rows
        else:
            raise Exception("sql must be a SELECT statement")

    def commitThread(self):
        "create a PostgreSQL cursor"
        try:
            self.__conn.commit()
        except psycopg2.ProgrammingError as e:
            #print e.message
            raise e
        except Exception as e:
            raise e
            
    def rollbackThread(self):
        "create a PostgreSQL cursor"
        try:
            self.__conn.rollback()
        except psycopg2.ProgrammingError as e:
            print e.message
    
    def executeInThread(self,sql):
        cur = self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            cur.execute(sql)
        except psycopg2.ProgrammingError as e:
            print e.message
            self.__conn.rollback()
            raise e
        except Exception as e:
            raise e
        try:
            rows = cur.fetchall()
        except:
            rows = None
        cur.close()
        return rows
                
    def execute(self,sql):
        cur = self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            cur.execute(sql)
        
        except psycopg2.ProgrammingError as e:
            print e.message
       
        #except e:
        #    raise e
        try:
            rows = cur.fetchall()
        except:
            rows = None
        self.__conn.commit()
        return rows

    def insertMany(self,sql,dict):
        cur = self.__conn.cursor()
        try:
            cur.executemany(sql,dict)
        except psycopg2.ProgrammingError as e:
            print e.message
        self.__conn.commit()
        return
        
