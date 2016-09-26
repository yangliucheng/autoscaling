#!/usr/bin/env python
#coding=utf-8

import logging

from db_operation import *

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S')

def query_conf(marathon,app):
    """
    :marathon marathon name
    :app_id app id
    """
    db=DB()
    sql="select * from app_scale_rule where marathon_name='{}' and app_id='{}'".format(marathon,app)
    conn=db.connect_mysql()
    result=db.select_mysql(conn,sql)
    logging.debug("in query_conf:{}".format(result))
    return result
def cpu_get(marathon,app,cpu):
    """
    :marathon marathon name
    :app app id
    :cpu the flag that judge the cpu configuration
    """
    db=DB()
    conn=db.connect_mysql()
    if cpu==1:
        sql="select max_threshold,min_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='cpu'".format(marathon,app)
        result=db.select_mysql(conn,sql)
        db.close_mysql(conn)
        return result
    else:
        db.close_mysql(conn)
        return None
def mem_get(marathon,app,mem):
    """
    :marathon marathon name
    :app app id
    :mem the flag that judge the cpu configuration
    """
    db=DB()
    conn=db.connect_mysql()
    if mem==1:
        sql="select max_threshold,min_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='memory'".format(marathon,app)
        result=db.select_mysql(conn,sql)
        return result
    else:
        return None
def thread_get(marathon,app,thread):
    """
    :marathon marathon name
    :app app id
    :thread the flag that judge the cpu configuration
    """
    db=DB()
    conn=db.connect_mysql()
    if thread==1:
        sql="select max_threshold,min_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='thread'".format(marathon,app)
        result=db.select_mysql(conn,sql)
        return result
    else:
        return None
def request_queue_get(marathon,app,mem):
    """
    :marathon marathon name
    :app app id
    :request_queue the flag that judge the cpu configuration
    """
    db=DB()
    conn=db.connect_mysql()
    if mem==1:
        sql="select max_threshold,min_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='request_queue'".format(marathon,app)
        result=db.select_mysql(conn,sql)
        return result
    else:
        return None
        

if __name__=="__main__":
    #results=query_conf('marathon','test1')
    #print(results)
    cpu=cpu_get('marathon','test',1)
    print cpu
    """
    for result in results:
        print(result)
        for item in result:
            print(item)
    """
    
    #result=mem_get('marathon','test',0)
    #print result
    """
    resultl=result[0]
    for item in resultl:
        print(item)
    """
