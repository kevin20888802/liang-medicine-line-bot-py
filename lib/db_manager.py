import psycopg2
import os

class PostgresBaseManager:

    def __init__(self,local):

        self.database = 'postgres'
        self.user = 'postgres'
        self.password = '1234'
        self.host = 'localhost'
        self.port = '5432'
        self.localTest = local
        self.conn = self.connect()
    pass

    def connect(self):
        """
        :return: 連接 Heroku Postgres SQL 認證用
        """
        if self.localTest == True:
            conn = psycopg2.connect(
                database=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port)
            conn.autocommit = True
            return conn
        else:
            conn = psycopg2.connect(os.environ['DATABASE_URL'])
            conn.autocommit = True
            return conn
        pass
    pass

    def disconnect(self):
        """
        :return: 關閉資料庫連線使用
        """
        self.conn.close()
    pass

    def testConnection(self):
        """
        :return: 測試是否可以連線到 Heroku Postgres SQL
        """
        cur = self.conn.cursor()
        cur.execute('SELECT VERSION()')
        results = cur.fetchall()
        print("Database version : {0} ".format(results))
        self.conn.commit()
        cur.close()
    pass

    # 執行 sql 指令
    def execute(self,cmd):
        cur = self.conn.cursor()
        cur.execute("set transaction read write;")
        cur.execute(cmd)
        self.conn.commit()
        if cmd.startswith("Select") and (cur.rowcount > 0):
            results = cur.fetchall()
            cur.close()
            return results
        else:
            return None
        pass
    pass

    # 執行 sql 檔案
    def executeFile(self,path):
        cur = self.conn.cursor()
        sql_file = open(path,'r',encoding="utf-8")
        cur.execute("set transaction read write;")
        cur.execute(sql_file.read())
        self.conn.commit()
    pass
pass