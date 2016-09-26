#!/usr/bin/env python
#coding=utf-8
import logging
import os

import mysql.connector

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S')



class DB(object):
    """
    :Some operations about databases
    """
    def __init__(self):
        logging.debug("DB init....")
        self.db_user = os.environ.get('DB_USER', 'root')
        self.db_pass = os.environ.get('DB_PASS', 'root')
        self.db_host = os.environ.get('DB_HOST', '192.168.1.11')
        self.db_port = os.environ.get('DB_PORT', 3366)
        self.db_name = os.environ.get('DB_NAME', 'scale')
        self.config = {
            'user': self.db_user,
            'password': self.db_pass,
            'host': self.db_host,
            'port': self.db_port,
            'database': self.db_name,
            'charset': 'utf8'}
        logging.debug("The config:{}".format(self.config))
    def connect_mysql(self):
        try:
            logging.debug("config in connect_mysql():{}".format(self.config))
            conn=mysql.connector.connect(**self.config)
            return conn
        except Exception as e:
            logging.debug(e)
    def select_mysql(self,conn,sql):
        logging.debug("sql={}".format(sql))
        try:
            cur=conn.cursor()
            cur.execute(sql)
            return cur.fetchall()
        except Exception as e:
            cur.close()
            conn.close()
            logging.debug(e)
        else:
            cur.close()
    def insert_mysql(self,conn,sql):
        logging.debug("sql={}".format(sql))
        try:
            cur=conn.cursor()
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            cur.close()
            conn.close()
            logging.debug(e)
        else:
            cur.close()
    def update_mysql(self,conn,sql):
        logging.debug("sql={}".format(sql))
        try:
            cur=conn.cursor()
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            cur.close()
            conn.close()
            logging.debug(e)
        else:
            cur.close()
    def delete_mysql(self,conn,sql):
        logging.debug("sql={}".format(sql))
        try:
            cur=conn.cursor()
            cur.execute(sql)
        except Exception as e:
            cur.close()
            conn.close()
            logging.debug(e)
        else:
            cur.close()
    def close_mysql(self,conn):
        try:
            conn.close()
        except Exception as e:
            logging.debug(e)


        



if __name__=="__main__":
    db=DB()
    conn=db.connect_mysql()
    result=db.select_mysql(conn,"select * from quota_info")
    print(result)
