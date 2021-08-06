import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import urllib.parse as urlparse

class PostgresBaseManager:

    def __init__(self,local):

        self.database = 'postgres'
        self.user = 'postgres'
        self.password = '1234'
        self.host = 'localhost'
        self.port = '5432'
        self.localTest = local
        self.conn = self.connect()
        self.setupSQLCMD = """-- 使用者藥品表
--Drop Table If Exists UserMedicine;
Create Table If Not Exists UserMedicine
(
    ID int GENERATED ALWAYS AS IDENTITY Primary Key,
    UserID varchar(1024),
    MedicineName varchar(1024),
    Amount int,
    TakeAmount int
);

-- 提醒時間表
--Drop Table If Exists Notify;
Create Table If Not Exists Notify 
(
    ID int GENERATED ALWAYS AS IDENTITY Primary Key,
    UserID varchar(1024),
    Description text,
    TargetMedicine varchar(1024),
    TargetTime varchar(128),
    LastNotifyDate varchar(512),
    TakeDate varchar(512)
);

-- 吃藥紀錄表
--Drop Table If Exists TakeMedicineHistory;
Create Table If Not Exists TakeMedicineHistory 
(
    ID int GENERATED ALWAYS AS IDENTITY Primary Key,
    UserID varchar(1024),
    Description text,
    AnwTime varchar(128)
);

-- 使用者狀態表
--Drop Table If Exists UserStatus;
Create Table If Not Exists UserStatus 
(
    UserID varchar(1024) Primary Key,
    Stat varchar(1024),
    TempValue text
);
    """
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
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            return conn
        else:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            print(DATABASE_URL)
            cur = self.conn.cursor()
            cur.execute('SELECT VERSION()')
            results = cur.fetchall()
            print("Database version : {0} ".format(results))
            conn.autocommit = True
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
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
        print("running sql file:" + path)
        cur.execute(sql_file.read())
        self.conn.commit()
    pass
pass