#!/usr/bin/env python
#coding=utf-8

from bottle import Bottle,request
import json
import logging

from db_operation import *
from set_get import *

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S')
app=Bottle()

@app.route('/applist/:marathon_name',method=['GET','POST'])
def app_list(marathon_name):
    """
    :marathon_name 
    """
    ret={
            "status":"",
            "msg":"",
            "apps":""
            }
    apps=[]
    sql="select app_id from app_scale_rule where marathon_name='{}'".format(marathon_name)
    #print(sql)
    try:
        logging.debug("Connecting DB...")
        db=DB()
        conn=db.connect_mysql()
        results=db.select_mysql(conn,sql)
        logging.debug(results)
    

        for result in results:
            app={}
            sqlapp="select scale_type from app_scale_rule where marathon_name='{}' and app_id='{}'".format(marathon_name,result[0])
            r_scale_type=db.select_mysql(conn,sqlapp)
            logging.debug("r_scale:{}".format(r_scale_type))
            if r_scale_type!=None and r_scale_type!=[]:
                r_switch=db.select_mysql(conn,"select switch from app_scale_rule where marathon_name='{}' and app_id='{}'".format(marathon_name,result[0]))
                logging.debug("r_switch:{}".format(list(r_switch)))
                if (1,) in list(r_switch):
                    app["status"]=1
                    app["app_id"]=result[0]
                else:
                    app["status"]=0
                    app["app_id"]=result[0]
            else:
                app["status"]=-1
                app["app_id"]=result[0]
            sqlstatus="select count_status,event from scale_log where marathon_name='{}' and app_id='{}' order by time desc limit 1".format(marathon_name,result[0])
            r_count_status=db.select_mysql(conn,sqlstatus)
            logging.debug("query count_status from scale_log:{}".format(r_count_status))
            print(r_count_status==[],r_count_status)
            if r_count_status!=[] and r_count_status!=None:
                app["count_status"]=str(r_count_status[0][0])
                app["event_description"]=str(r_count_status[0][1])
            else:
                app["count_status"]=""
                app["event_description"]=""
            if app in apps:
                continue
            else:
                apps.append(app)
            ret["status"]="OK"
            ret["msg"]="query applist successful"
            ret["apps"]=apps
            logging.debug("ret:{}".format(ret))
    except Exception as e:
        ret["status"]="NOT OK"
        ret["msg"]="DB connect failed..."
        logging.error(e)
        return ret
    return ret
@app.route('/appinfo/:marathon_name/:app_id',method=['GET','POST'])
def app_info(marathon_name,app_id):
    ret={
            "status":"",
            "result":"",
            "msg":""
            }
    result={
            "marathon_id":marathon_name,
            "app_id":app_id,
            "status":"",
            "count_status":"",
            "event_description":"",
            "scale_up":{
                "status":"",
                "mem":"",
                "cpu":"",
                "thread":"",
                "request_queue":"",
                "collect_period":"",
                "continue_period":"",
                "cool_down_period":"",
                "scale_amount":"",
                "max_scale_amount":""
                },
            "scale_down":{
                "status":"",
                "mem":"",
                "cpu":"",
                "thread":"",
                "request_queue":"",
                "collect_period":"",
                "continue_period":"",
                "cool_down_period":"",
                "scale_amount":"",
                "max_scale_amount":""
                }
            }
    db=DB()
    conn=db.connect_mysql()

    try:
        conf=query_conf(marathon_name,app_id)
        logging.debug("conf in app_info:{}".format(conf))
        #print("len(conf):",len(conf))
        if conf!=[] and conf!=None:
            r_switch=db.select_mysql(conn,"select switch from app_scale_rule where marathon_name='{}' and app_id='{}'".format(marathon_name,app_id))
            logging.debug("r_switch:{}".format(r_switch))
            if (1,) in list(r_switch):
                result["status"]=1
            else:
                result["status"]=0

        else:
            result["status"]=-1
        status_event=db.select_mysql(conn,"select count_status,event from scale_log where marathon_name='{}' and app_id='{}' order by time desc limit 1".format(marathon_name,app_id))
        logging.debug("status_event:{}".format(status_event))
        if status_event!=[] and status_event!=None:
            result["count_status"]=str(status_event[0][0])
            result["event_description"]=str(status_event[0][1])
        r_up=db.select_mysql(conn,"select * from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))
        logging.debug("r_up:{}".format(r_up))
        if r_up!=[] and r_up!=None:
            result["scale_up"]["collect_period"]=r_up[0][11]
            result["scale_up"]["continue_period"]=r_up[0][12]
            result["scale_up"]["cool_down_period"]=r_up[0][10]
            result["scale_up"]["scale_amount"]=r_up[0][4]
            result["scale_up"]["max_scale_amount"]=r_up[0][3]

            if r_up[0][9]==1:
                result["scale_up"]["status"]=1
            else:
                result["scale_up"]["status"]=0

            if r_up[0][5]==1:
                r_mem=db.select_mysql(conn,"select max_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='memory'".format(marathon_name,app_id))
                logging.debug("r_mem:{}".format(r_mem))
                #logging.debug("r_mem[0][0]:{}".format(r_mem[0][0]))
                if r_mem!=[] and r_mem!=None:
                    result["scale_up"]["mem"]=r_mem[0][0]
            if r_up[0][6]==1:
                r_cpu=db.select_mysql(conn,"select max_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='cpu'".format(marathon_name,app_id))
                logging.debug("r_cpu:{}".format(r_cpu))
                if r_cpu:
                    logging.debug("r_cpu[0][0]:{}".format(r_cpu[0][0]))
                    result["scale_up"]["cpu"]=r_cpu[0][0]
            if r_up[0][7]==1:
                r_thread=db.select_mysql(conn,"select max_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='thread'".format(marathon_name,app_id))
                logging.debug("r_thread:{}".format(r_thread))
                if r_thread!=[] and r_thread!=None:
                    logging.debug("r_thread[0][0]:{}".format(r_thread[0][0]))
                    result["scale_up"]["thread"]=r_thread[0][0]
            if r_up[0][8]==1:
                r_ha_queue=db.select_mysql(conn,"select max_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='ha_queue'".format(marathon_name,app_id))
                logging.debug("r_ha_queue:{}".format(r_ha_queue))
                if r_ha_queue:
                    logging.debug("r_ha_queue[0][0]:{}".format(r_ha_queue[0][0]))
                    result["scale_up"]["ha_queue"]=r_ha_queue[0][0]
        r_down=db.select_mysql(conn,"select * from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))
        logging.debug("r_down:{}".format(r_down))

        if r_down!=[] and r_down!=None:
            result["scale_down"]["collect_period"]=r_down[0][11]
            result["scale_down"]["continue_period"]=r_down[0][12]
            result["scale_down"]["cool_down_period"]=r_down[0][10]
            result["scale_down"]["scale_amount"]=r_down[0][4]
            result["scale_down"]["max_scale_amount"]=r_down[0][3]
            if r_down[0][9]==1:
                result["scale_down"]["status"]=1
            else:
                result["scale_down"]["status"]=0

            if r_up[0][5]==1:
                r_mem=db.select_mysql(conn,"select min_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='memory'".format(marathon_name,app_id))
                logging.debug("r_mem:{}".format(r_mem))
                logging.debug("r_mem[0][0]:{}".format(r_mem[0][0]))
                if r_mem!=[] and r_mem!=None:
                    result["scale_down"]["mem"]=r_mem[0][0]
            if r_up[0][6]==1:
                r_cpu=db.select_mysql(conn,"select min_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='cpu'".format(marathon_name,app_id))
                logging.debug("r_cpu:{}".format(r_cpu))
                if r_cpu!=[] and r_cpu!=None:
                    logging.debug("r_cpu[0][0]:{}".format(r_cpu[0][0]))
                    result["scale_down"]["cpu"]=r_cpu[0][0]
            if r_up[0][7]==1:
                r_thread=db.select_mysql(conn,"select min_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='thread'".format(marathon_name,app_id))
                logging.debug("r_thread:{}".format(r_thread))
                if r_thread!=[] and r_thread!=None:
                    logging.debug("r_thread[0][0]:{}".format(r_thread[0][0]))
                    result["scale_down"]["thread"]=r_thread[0][0]
            if r_up[0][8]==1:
                r_ha_queue=db.select_mysql(conn,"select min_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='ha_queue'".format(marathon_name,app_id))
                logging.debug("r_ha_queue:{}".format(r_ha_queue))
                if r_ha_queue!=[] and r_ha_queue!=None:
                    logging.debug("r_ha_queue[0][0]:{}".format(r_ha_queue[0][0]))
                    result["scale_down"]["ha_queue"]=r_ha_queue[0][0]
        ret["status"]="OK"
        result1={
                "marathon_id":marathon_name,
                "app_id":app_id,
                "scale_up":{
                    "mem":result["scale_up"]["mem"],
                    "cpu":result["scale_up"]["cpu"],
                    "thread":result["scale_up"]["thread"],
                    "request_queue":result["scale_up"]["request_queue"],
                    "collect_period":result["scale_up"]["collect_period"],
                    "continue_period":result["scale_up"]["continue_period"],
                    "cool_down_period":result["scale_up"]["cool_down_period"],
                    "scale_amount":result["scale_up"]["scale_amount"],
                    "max_scale_amount":result["scale_up"]["max_scale_amount"]
                    },
                "scale_down":{
                    "mem":result["scale_down"]["mem"],
                    "cpu":result["scale_down"]["cpu"],
                    "thread":result["scale_down"]["thread"],
                    "request_queue":result["scale_down"]["request_queue"],
                    "collect_period":result["scale_down"]["collect_period"],
                    "continue_period":result["scale_down"]["continue_period"],
                    "cool_down_period":result["scale_down"]["cool_down_period"],
                    "scale_amount":result["scale_down"]["scale_amount"],
                    "max_scale_amount":result["scale_down"]["max_scale_amount"]
                    }
                }
        ret["result"]=result1
        ret["msg"]="app info query successful."
    except Exception as e:
        ret["status"]="NOT OK"
        ret["msg"]="app info query failed."
        logging.debug(e)
    return ret

@app.route('/ruleset',method=['GET','POST'])
def rule_set():
    result={
            "status":""
            }
    try:
        rule=json.loads(request.body.read())
        print("rule:",rule)
        db=DB()
        conn=db.connect_mysql()
        marathon_name=rule["marathon_id"]
        print("marathon_name:",marathon_name)
        app_id=rule["app_id"]
        scale_up=rule["scale_up"]
        print("=============================================scale_up mem===========================================================")
        print(scale_up["mem"])
        print("scale_up:",scale_up)
        print(scale_up!=None)
        if scale_up!=None and scale_up!=[] and scale_up!="":
            up_status=1
            up_scale_type='up'
            if scale_up["mem"]!=None and scale_up["mem"]!=0 and scale_up["mem"]!="":
                up_mem=1
                max_mem=db.select_mysql(conn,"select max_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='memory'".format(marathon_name,app_id))
                if max_mem!=[] and max_mem!=None:
                    db.update_mysql(conn,"update quota_info set max_threshold={} where marathon_name='{}' and app_id='{}' and rule_type='memory'".format(scale_up["mem"],marathon_name,app_id))
                    #db.delete_mysql(conn,"delete from quota_info where marathon_name='{}' and app_id='{}' and rule_type='memory'".format(marathon_name,app_id))
                else:
                    #db.delete_mysql(conn,"delete from quota_info where marathon_name='{}' and app_id='{}' and rule_type='memory'".format(marathon_name,app_id))
                    db.insert_mysql(conn,"insert into quota_info(marathon_name,app_id,rule_type,max_threshold) values('{}','{}','memory','{}')".format(marathon_name,app_id,scale_up["mem"]))
            else:
                up_mem=0
            #up_cpu=scale_up["cpu"]
            logging.debug("scale_up cup:{}".format(scale_up["cpu"]))
            print(scale_up["cpu"]=="")
            if scale_up["cpu"]!=None and scale_up["cpu"]!=0 and scale_up["cpu"]!="":
                up_cpu=1
                max_cpu=db.select_mysql(conn,"select max_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='cpu'".format(marathon_name,app_id))
                if max_cpu!=[] and max_cpu!=None:
                    db.update_mysql(conn,"update quota_info set max_threshold={} where marathon_name='{}' and app_id='{}' and rule_type='cpu'".format(scale_up["cpu"],marathon_name,app_id))
                    #db.delete_mysql(conn,"delete from quota_info where marathon_name='{}' and app_id='{}' and rule_type='cpu'".format(marathon_name,app_id))
                else:
                    db.insert_mysql(conn,"insert into quota_info(marathon_name,app_id,rule_type,max_threshold) values('{}','{}','cpu','{}')".format(marathon_name,app_id,scale_up["cpu"]))
            else:
                up_cpu=0
            #up_thread=scale_up["thread"]
            if scale_up["thread"]!=None and scale_up["thread"]!=0 and scale_up["thread"]!="":
                up_thread=1
                max_thread=db.select_mysql(conn,"select max_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='thread'".format(marathon_name,app_id))
                if max_thread!=[] and max_thread!=None:
                    db.update_mysql(conn,"update quota_info set max_threshold={} where marathon_name='{}' and app_id='{}' and rule_type='thread'".format(scale_up["thread"],marathon_name,app_id))
                    #db.delete_mysql(conn,"delete from quota_info where marathon_name='{}' and app_id='{}' and rule_type='cpu'".format(marathon_name,app_id))
                else:
                    db.insert_mysql(conn,"insert into quota_info(marathon_name,app_id,rule_type,max_threshold) values('{}','{}','thread','{}')".format(marathon_name,app_id,scale_up["thread"]))
            else:
                up_thread=0
            #up_ha_queue=scale_up["request_queue"]
            if scale_up["request_queue"]!=None and scale_up["request_queue"]!=0 and scale_up["request_queue"]!="":
                up_ha_queue=1
                max_queue=db.select_mysql(conn,"select max_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='ha_queue'".format(marathon_name,app_id))
                if max_queue!=[] and max_queue!=None:
                    db.update_mysql(conn,"update quota_info set max_threshold={} where marathon_name='{}' and app_id='{}' and rule_type='ha_queue'".format(scale_up["request_queue"],marathon_name,app_id))
                    #db.delete_mysql(conn,"delete from quota_info where marathon_name='{}' and app_id='{}' and rule_type='cpu'".format(marathon_name,app_id))
                else:
                    db.insert_mysql(conn,"insert into quota_info(marathon_name,app_id,rule_type,max_threshold) values('{}','{}','ha_queue','{}')".format(marathon_name,app_id,scale_up["request_queue"]))
            else:
                up_ha_queue=0
            #up_collect_period=scale_up["collect_period"]
            if scale_up["collect_period"]!="" and scale_up["collect_period"]!=" " and scale_up["collect_period"]!=None:
                up_collect_period=scale_up["collect_period"]
            else:
                up_collect_period=0
            if scale_up["continue_period"]!="" and scale_up["continue_period"]!=" " and scale_up["continue_period"]!=None:
                up_continue_period=scale_up["continue_period"]
            else:
                up_continue_period=0
            if scale_up["cool_down_period"]!="" and scale_up["cool_down_period"]!=" " and scale_up["cool_down_period"]!=None:
                up_cold_down_period=scale_up["cool_down_period"]
            else:
                up_cold_down_period=0
            if scale_up["scale_amount"]!="" and scale_up["scale_amount"]!=" " and scale_up["scale_amount"]!=None:
                up_scale_amount=scale_up["scale_amount"]
            else:
                up_scale_amount=0
            if scale_up["max_scale_amount"]!="" and scale_up["max_scale_amount"]!=" " and scale_up["max_scale_amount"]!=None:
                up_max_scale_amount=scale_up["max_scale_amount"]
            else:
                up_max_scale_amount=0
            query_r=db.select_mysql(conn,"select * from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))
            logging.debug("query_r:".format(query_r))
            if query_r!=[] and query_r!=None:
                db.delete_mysql(conn,"delete from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))

            sqlup="insert into app_scale_rule(marathon_name,app_id,scale_type,scale_threshold,per_auto_scale,memory,cpu,thread,ha_queue,switch,cold_time,collect_period,continue_period) values('{}','{}','{}',{},{},{},{},{},{},{},{},{},{})".format(marathon_name,app_id,up_scale_type,up_max_scale_amount,up_scale_amount,up_mem,up_cpu,up_thread,up_ha_queue,up_status,up_cold_down_period,up_collect_period,up_continue_period)
            logging.debug("sqlup:{}".format(sqlup))
            db.insert_mysql(conn,sqlup)
            result["status"]="OK"
        scale_down=rule["scale_down"]
        print("scale_down:",scale_down)
        print(scale_down!=None)
        if scale_down!=None:
            d_status=1
            d_scale_type='down'
            #d_mem=scale_down["mem"]
            if scale_down["mem"]!=None and scale_down["mem"]!=0 and scale_down["mem"]!="":
                d_mem=1
                d_max_mem=db.select_mysql(conn,"select min_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='memory'".format(marathon_name,app_id))
                if d_max_mem!=[] and d_max_mem!=None:
                    db.update_mysql(conn,"update quota_info set min_threshold={} where marathon_name='{}' and app_id='{}' and rule_type='memory'".format(scale_down["mem"],marathon_name,app_id))
                    #db.delete_mysql(conn,"delete from quota_info where marathon_name='{}' and app_id='{}' and rule_type='memory'".format(marathon_name,app_id))
                else:
                    #db.delete_mysql(conn,"delete from quota_info where marathon_name='{}' and app_id='{}' and rule_type='memory'".format(marathon_name,app_id))
                    db.insert_mysql(conn,"insert into quota_info(marathon_name,app_id,rule_type,min_threshold) values('{}','{}','memory','{}')".format(marathon_name,app_id,scale_down["mem"]))
            else:
                d_mem=0
            #d_cpu=scale_down["cpu"]
            if scale_down["cpu"]!=None and scale_down["cpu"]!=0 and scale_down["cpu"]!="":
                d_cpu=1
                d_max_cpu=db.select_mysql(conn,"select max_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='cpu'".format(marathon_name,app_id))
                if d_max_cpu!=[] and d_max_cpu!=None:
                    db.update_mysql(conn,"update quota_info set min_threshold={} where marathon_name='{}' and app_id='{}' and rule_type='cpu'".format(scale_down["cpu"],marathon_name,app_id))
                    #db.delete_mysql(conn,"delete from quota_info where marathon_name='{}' and app_id='{}' and rule_type='cpu'".format(marathon_name,app_id))
                else:
                    db.insert_mysql(conn,"insert into quota_info(marathon_name,app_id,rule_type,min_threshold) values('{}','{}','cpu','{}')".format(marathon_name,app_id,scale_down["cpu"]))
            else:
                d_cpu=0
            #d_thread=scale_down["thread"]
            if scale_down["thread"]!=None and scale_down["thread"]!=0 and scale_down["thread"]!="":
                d_thread=1
                d_max_thread=db.select_mysql(conn,"select min_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='thread'".format(marathon_name,app_id))
                if d_max_thread!=None and d_max_thread!=[]:
                    db.update_mysql(conn,"update quota_info set min_threshold={} where marathon_name='{}' and app_id='{}' and rule_type='thread'".format(scale_down["thread"],marathon_name,app_id))
                    #db.delete_mysql(conn,"delete from quota_info where marathon_name='{}' and app_id='{}' and rule_type='cpu'".format(marathon_name,app_id))
                else:
                    db.insert_mysql(conn,"insert into quota_info(marathon_name,app_id,rule_type,min_threshold) values('{}','{}','thread','{}')".format(marathon_name,app_id,scale_down["thread"]))
            else:
                d_thread=0
            #d_ha_queue=scale_down["request_queue"]
            if scale_down["request_queue"]!=None and scale_down["request_queue"]!=0 and scale_down["request_queue"]!="":
                d_ha_queue=1
                d_max_queue=db.select_mysql(conn,"select min_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='ha_queue'".format(marathon_name,app_id))
                if d_max_queue!=[] and d_max_queue!=None:
                    db.update_mysql(conn,"update quota_info set min_threshold={} where marathon_name='{}' and app_id='{}' and rule_type='ha_queue'".format(scale_down["request_queue"],marathon_name,app_id))
                    #db.delete_mysql(conn,"delete from quota_info where marathon_name='{}' and app_id='{}' and rule_type='cpu'".format(marathon_name,app_id))
                else:
                    db.insert_mysql(conn,"insert into quota_info(marathon_name,app_id,rule_type,min_threshold) values('{}','{}','ha_queue','{}')".format(marathon_name,app_id,scale_down["request_queue"]))
            else:
                d_ha_queue=0
            if scale_down["collect_period"]!="" and scale_down["collect_period"]!=" " and scale_down["collect_period"]!=None:
                d_collect_period=scale_down["collect_period"]
            else:
                d_collect_period=0
            if scale_down["continue_period"]!="" and scale_down["continue_period"]!=" " and scale_down["continue_period"]!=None:
                d_continue_period=scale_down["continue_period"]
            else:
                d_continue_period=0
            if scale_down["cool_down_period"]!="" and scale_down["cool_down_period"]!=" " and scale_down["cool_down_period"]!=None:
                d_cold_down_period=scale_down["cool_down_period"]
            else:
                d_cold_down_period=0
            if scale_down["scale_amount"]!="" and scale_down["scale_amount"]!=" " and scale_down["scale_amount"]!=None:
                d_scale_amount=scale_down["scale_amount"]
            else:
                d_scale_amount=0
            if scale_down["max_scale_amount"]!="" and scale_down["max_scale_amount"]!=" " and scale_down["max_scale_amount"]!=None:
                d_max_scale_amount=scale_down["max_scale_amount"]
            else:
                d_max_scale_amount=0
            #d_collect_period=scale_down["collect_period"]
            #d_continue_period=scale_down["continue_period"]
            #d_cold_down_period=scale_down["cool_down_period"]
            #d_scale_amount=scale_down["scale_amount"]
            #d_max_scale_amount=scale_down["max_scale_amount"]
            d_query_r=db.select_mysql(conn,"select * from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))
            logging.debug("d_query_r:".format(d_query_r))
            if d_query_r!=[] and d_query_r!=None:
                db.delete_mysql(conn,"delete from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))

            sqld="insert into app_scale_rule(marathon_name,app_id,scale_type,scale_threshold,per_auto_scale,memory,cpu,thread,ha_queue,switch,cold_time,collect_period,continue_period) values('{}','{}','{}',{},{},{},{},{},{},{},{},{},{})".format(marathon_name,app_id,d_scale_type,d_max_scale_amount,d_scale_amount,d_mem,d_cpu,d_thread,d_ha_queue,d_status,d_cold_down_period,d_collect_period,d_continue_period)
            logging.debug("sqld:{}".format(sqld))
            db.insert_mysql(conn,sqld)
            result["status"]="OK"

    except Exception as e:
        logging.debug(e)
        result["status"]="NOT OK"
    return result





@app.route('/ruleupdate',method=['GET','POST'])
def rule_update():
    result={
            "status":"",
            "msg":""
            }
    try:
        rule=json.loads(request.body.read())
        print("rule:",rule)
        db=DB()
        conn=db.connect_mysql()
        marathon_name=rule["marathon_id"]
        print("marathon_name:",marathon_name)
        app_id=rule["app_id"]
        scale_up=rule["scale_up"]
        logging.debug("scale_up:{}".format(scale_up))
        print(scale_up!=None)
        if scale_up!=None:
            if scale_up["collect_period"]!="":
                up_cp=db.select_mysql(conn,"select collect_period from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))
                if up_cp!=None and up_cp!=[]:
                    db.update_mysql(conn,"update app_scale_rule set collect_period={},switch=1 where marathon_name='{}' and app_id='{}' and scale_type='up'".format(scale_up["collect_period"],marathon_name,app_id))
                else:
                    result["status"]="NOT OK"
                    result["msg"]="scale_up:collect_period of {}:{} not setted.".format(marathon_name,app_id)
                    return result
            if scale_up["continue_period"]!="":
                up_ctp=db.select_mysql(conn,"select continue_period from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))
                if up_ctp!=None and up_ctp!=[]:
                    db.update_mysql(conn,"update app_scale_rule set continue_period={},switch=1 where marathon_name='{}' and app_id='{}' and scale_type='up'".format(scale_up["continue_period"],marathon_name,app_id))
                else:
                    result["status"]="NOT OK"
                    result["msg"]="scale_up:continue_period of {}:{} not setted.".format(marathon_name,app_id)
                    return result
            if scale_up["cool_down_period"]!="":
                up_cd=db.select_mysql(conn,"select cold_time from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))
                if up_cd!=None and up_cd!=[]:
                    db.update_mysql(conn,"update app_scale_rule set cold_time={},switch=1 where marathon_name='{}' and app_id='{}' and scale_type='up'".format(scale_up["cool_down_period"],marathon_name,app_id))
                else:
                    result["status"]="NOT OK"
                    result["msg"]="scale_up:cool_time of {}:{} not setted.".format(marathon_name,app_id)
                    return result
            if scale_up["scale_amount"]!="":
                up_sa=db.select_mysql(conn,"select per_auto_scale from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))
                if up_sa!=None and up_sa!=[]:
                    db.update_mysql(conn,"update app_scale_rule set per_auto_scale={},switch=1 where marathon_name='{}' and app_id='{}' and scale_type='up'".format(scale_up["scale_amount"],marathon_name,app_id))
                else:
                    result["status"]="NOT OK"
                    result["msg"]="scale_up:per_auto_scale of {}:{} not setted.".format(marathon_name,app_id)
                    return result
            if scale_up["max_scale_amount"]!="":
                up_ms=db.select_mysql(conn,"select scale_threshold from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))
                if up_ms!=None and up_ms!=[]:
                    db.update_mysql(conn,"update app_scale_rule set scale_threshold={},switch=1 where marathon_name='{}' and app_id='{}' and scale_type='up'".format(scale_up["max_scale_amount"],marathon_name,app_id))
                else:
                    result["status"]="NOT OK"
                    result["msg"]="scale_up:scale_threshold of {}:{} not setted.".format(marathon_name,app_id)
                    return result
            if scale_up["mem"]!=None and scale_up["mem"]!="" and scale_up["mem"]!=0:
                up_mem=db.select_mysql(conn,"select memory from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))
                logging.debug("up_mem:{}".format(up_mem))
                if up_mem!=None and up_mem!=[]:
                    db.update_mysql(conn,"update app_scale_rule set memory=1,switch=1 where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))
                    q_mem=db.select_mysql(conn,"select max_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='memory'".format(marathon_name,app_id))
                    if q_mem!=None and q_mem!=[]:
                        db.update_mysql(conn,"update quota_info set max_threshold={} where marathon_name='{}' and app_id='{}' and rule_type='memory'".format(scale_up["mem"],marathon_name,app_id))
                    else:
                        result["status"]="NOT OK"
                        result["msg"]="{}:{} memory in quota_info not setted".format(marathon_name,app_id)
                else:
                    result["status"]="NOT OK"
                    result["msg"]="scale_up mem of {} {} not setted!".format(marathon_name,app_id)
                    return result
            if scale_up["cpu"]!=None and scale_up["cpu"]!="" and scale_up["cpu"]!=0:
                up_cpu=db.select_mysql(conn,"select cpu from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))
                logging.debug("up_cpu:{}".format(up_cpu))
                if up_cpu!=None and up_cpu!=[]:
                    db.update_mysql(conn,"update app_scale_rule set cpu=1,switch=1 where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))
                    q_cpu=db.select_mysql(conn,"select max_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='cpu'".format(marathon_name,app_id))
                    if q_cpu!=None and q_cpu!=[]:
                        db.update_mysql(conn,"update quota_info set max_threshold={} where marathon_name='{}' and app_id='{}' and rule_type='cpu'".format(scale_up["cpu"],marathon_name,app_id))
                    else:
                        result["status"]="NOT OK"
                        result["msg"]="{}:{} cpu in quota_info not setted".format(marathon_name,app_id)
                        
                else:
                    result["status"]="NOT OK"
                    result["msg"]="scale_up cpu of {} {} not setted!".format(marathon_name,app_id)
                    return result
            if scale_up["thread"]!=None and scale_up["thread"]!="" and scale_up["thread"]!=0:
                up_thread=db.select_mysql(conn,"select thread from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))
                logging.debug("up_thread:{}".format(up_thread))
                if up_thread!=None and up_thread!=[]:
                    db.update_mysql(conn,"update app_scale_rule set thread=1,switch=1 where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))
                    q_thread=db.select_mysql(conn,"select max_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='thread'".format(marathon_name,app_id))
                    if q_thread!=None and q_thread!=[]:
                        db.update_mysql(conn,"update quota_info set max_threshold={} where marathon_name='{}' and app_id='{}' and rule_type='thread'".format(scale_up["thread"],marathon_name,app_id))
                    else:
                        result["status"]="NOT OK"
                        result["msg"]="{}:{} thread in quota_info not setted".format(marathon_name,app_id)
                        
                else:
                    result["status"]="NOT OK"
                    result["msg"]="scale_up thread of {} {} not setted!".format(marathon_name,app_id)
                    return result
            if scale_up["request_queue"]!=None and scale_up["request_queue"]!="" and scale_up["request_queue"]!=0:
                up_ha_queue=db.select_mysql(conn,"select ha_queue from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))
                logging.debug("up_ha_queue:{}".format(up_ha_queue))
                if up_ha_queue!=None and up_ha_queue!=[]:
                    db.update_mysql(conn,"update app_scale_rule set ha_queue=1,switch=1 where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))
                    q_ha_queue=db.select_mysql(conn,"select max_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='ha_queue'".format(marathon_name,app_id))
                    if q_ha_queue!=None and q_ha_queue!=[]:
                        db.update_mysql(conn,"update quota_info set max_threshold={} where marathon_name='{}' and app_id='{}' and rule_type='ha_queue'".format(scale_up["request_queue"],marathon_name,app_id))
                    else:
                        result["status"]="NOT OK"
                        result["msg"]="{}:{} ha_queue in quota_info not setted".format(marathon_name,app_id)
                        
                else:
                    result["status"]="NOT OK"
                    result["msg"]="scale_up ha_queue of {} {} not setted!".format(marathon_name,app_id)
                    return result
        scale_down=rule["scale_down"]
        logging.debug("scale_down:{}".format(scale_down))
        if scale_down!=None:
            if scale_down["collect_period"]!="":
                d_up_cp=db.select_mysql(conn,"select collect_period from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))
                if d_up_cp!=None and d_up_cp!=[]:
                    db.update_mysql(conn,"update app_scale_rule set collect_period={},switch=1 where marathon_name='{}' and app_id='{}' and scale_type='down'".format(scale_down["collect_period"],marathon_name,app_id))
                else:
                    result["status"]="NOT OK"
                    result["msg"]="scale_down:collect_period of {}:{} not setted.".format(marathon_name,app_id)
                    return result
            if scale_down["continue_period"]!="":
                d_up_ctp=db.select_mysql(conn,"select continue_period from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))
                if d_up_ctp!=None and d_up_ctp!=[]:
                    db.update_mysql(conn,"update app_scale_rule set continue_period={},switch=1 where marathon_name='{}' and app_id='{}' and scale_type='down'".format(scale_down["continue_period"],marathon_name,app_id))
                else:
                    result["status"]="NOT OK"
                    result["msg"]="scale_down:continue_period of {}:{} not setted.".format(marathon_name,app_id)
                    return result
            if scale_down["cool_down_period"]!="":
                d_up_cd=db.select_mysql(conn,"select cold_time from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))
                if d_up_cd!=None and d_up_cd!=[]:
                    db.update_mysql(conn,"update app_scale_rule set cold_time={},switch=1 where marathon_name='{}' and app_id='{}' and scale_type='down'".format(scale_down["cool_down_period"],marathon_name,app_id))
                else:
                    result["status"]="NOT OK"
                    result["msg"]="scale_down:cool_time of {}:{} not setted.".format(marathon_name,app_id)
                    return result
            if scale_down["scale_amount"]!="":
                d_up_sa=db.select_mysql(conn,"select per_auto_scale from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))
                if d_up_sa!=None and d_up_sa!=[]:
                    db.update_mysql(conn,"update app_scale_rule set per_auto_scale={},switch=1 where marathon_name='{}' and app_id='{}' and scale_type='down'".format(scale_down["scale_amount"],marathon_name,app_id))
                else:
                    result["status"]="NOT OK"
                    result["msg"]="scale_down:per_auto_scale of {}:{} not setted.".format(marathon_name,app_id)
                    return result
            if scale_down["max_scale_amount"]!="":
                d_up_ms=db.select_mysql(conn,"select scale_threshold from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))
                if d_up_ms!=None and d_up_ms!=[]:
                    db.update_mysql(conn,"update app_scale_rule set scale_threshold={},switch=1 where marathon_name='{}' and app_id='{}' and scale_type='down'".format(scale_down["max_scale_amount"],marathon_name,app_id))
                else:
                    result["status"]="NOT OK"
                    result["msg"]="scale_down:scale_threshold of {}:{} not setted.".format(marathon_name,app_id)
                    return result
            if scale_down["mem"]!=None and scale_down["mem"]!="" and scale_down["mem"]!=0:
                d_up_mem=db.select_mysql(conn,"select memory from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))
                logging.debug("d_up_mem:{}".format(d_up_mem))
                if d_up_mem!=None and d_up_mem!=[]:
                    db.update_mysql(conn,"update app_scale_rule set memory=1,switch=1 where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))
                    d_q_mem=db.select_mysql(conn,"select max_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='memory'".format(marathon_name,app_id))
                    if d_q_mem!=None and d_q_mem!=[]:
                        db.update_mysql(conn,"update quota_info set min_threshold={} where marathon_name='{}' and app_id='{}' and rule_type='memory'".format(scale_down["mem"],marathon_name,app_id))
                    else:
                        result["status"]="NOT OK"
                        result["msg"]="{}:{} memory in quota_info not setted".format(marathon_name,app_id)
                else:
                    result["status"]="NOT OK"
                    result["msg"]="scale_down mem of {} {} not setted!".format(marathon_name,app_id)
                    return result
            if scale_down["cpu"]!=None and scale_down["cpu"]!="" and scale_down["cpu"]!=0:
                d_up_cpu=db.select_mysql(conn,"select cpu from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))
                logging.debug("d_up_cpu:{}".format(d_up_cpu))
                if d_up_cpu!=None and d_up_cpu!=[]:
                    db.update_mysql(conn,"update app_scale_rule set cpu=1,switch=1 where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))
                    d_q_cpu=db.select_mysql(conn,"select min_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='cpu'".format(marathon_name,app_id))
                    if d_q_cpu!=None and d_q_cpu!=[]:
                        db.update_mysql(conn,"update quota_info set min_threshold={} where marathon_name='{}' and app_id='{}' and rule_type='cpu'".format(scale_down["cpu"],marathon_name,app_id))
                    else:
                        result["status"]="NOT OK"
                        result["msg"]="{}:{} cpu in quota_info not setted".format(marathon_name,app_id)
                        
                else:
                    result["status"]="NOT OK"
                    result["msg"]="scale_down cpu of {} {} not setted!".format(marathon_name,app_id)
                    return result
            if scale_down["thread"]!=None and scale_down["thread"]!="" and scale_down["thread"]!=0:
                d_up_thread=db.select_mysql(conn,"select thread from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))
                logging.debug("d_up_thread:{}".format(d_up_thread))
                if d_up_thread!=None and d_up_thread!=[]:
                    db.update_mysql(conn,"update app_scale_rule set thread=1,switch=1 where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))
                    d_q_thread=db.select_mysql(conn,"select min_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='thread'".format(marathon_name,app_id))
                    if d_q_thread!=None and d_q_thread!=[]:
                        db.update_mysql(conn,"update quota_info set min_threshold={} where marathon_name='{}' and app_id='{}' and rule_type='thread'".format(scale_down["thread"],marathon_name,app_id))
                    else:
                        result["status"]="NOT OK"
                        result["msg"]="{}:{} thread in quota_info not setted".format(marathon_name,app_id)
                        
                else:
                    result["status"]="NOT OK"
                    result["msg"]="scale_down thread of {} {} not setted!".format(marathon_name,app_id)
                    return result
            if scale_down["request_queue"]!=None and scale_down["request_queue"]!="" and scale_down["request_queue"]!=0:
                d_up_ha_queue=db.select_mysql(conn,"select ha_queue from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))
                logging.debug("d_up_ha_queue:{}".format(d_up_ha_queue))
                if d_up_ha_queue!=None and d_up_ha_queue!=[]:
                    db.update_mysql(conn,"update app_scale_rule set ha_queue=1,switch=1 where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))
                    d_q_ha_queue=db.select_mysql(conn,"select min_threshold from quota_info where marathon_name='{}' and app_id='{}' and rule_type='ha_queue'".format(marathon_name,app_id))
                    if d_q_ha_queue!=None and d_q_ha_queue!=[]:
                        db.update_mysql(conn,"update quota_info set min_threshold={} where marathon_name='{}' and app_id='{}' and rule_type='ha_queue'".format(scale_down["request_queue"],marathon_name,app_id))
                    else:
                        result["status"]="NOT OK"
                        result["msg"]="{}:{} ha_queue in quota_info not setted".format(marathon_name,app_id)
                        
                else:
                    result["status"]="NOT OK"
                    result["msg"]="scale_down ha_queue of {} {} not setted!".format(marathon_name,app_id)
                    return result
        result["status"]="OK"
        result["msg"]="update successfully."
        return result
    except Exception as e:
        logging.error(e)
@app.route('/pause/:marathon_name/:app_id',method=['GET','POST'])
def rule_pause(marathon_name,app_id):
    result={
            "status":"",
            "msgup":"",
            "msgdown":""
            }
    db=DB()
    conn=db.connect_mysql()
    try:
        up_r=db.select_mysql(conn,"select switch from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))
        if up_r!=None and up_r!=[]:
            db.update_mysql(conn,"update app_scale_rule set switch=0 where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))
            result["msgup"]="up rule pause successfu."
            result["status"]="OK"
        else:
            result["msgup"]="{}:{} the rule not setted.".format(marathon_name,app_id)
        down_r=db.select_mysql(conn,"select switch from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))
        if down_r!=None and down_r!=[]:
            db.update_mysql(conn,"update app_scale_rule set switch=0 where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))
            result["status"]="OK"
            result["msgdown"]="down rule pause successful"
        else:
            result["msgdown"]="{}:{} the rule not setted.".format(marathon_name,app_id)
        return result
    except Exception as e:
        reusult["status"]="NOT OK"
        logging.debug(e)
        return result
@app.route('/recover/:marathon_name/:app_id',method=['GET','POST'])
def rule_pause(marathon_name,app_id):
    result={
            "status":"",
            "msgup":"",
            "msgdown":""
            }
    db=DB()
    conn=db.connect_mysql()
    try:
        up_r=db.select_mysql(conn,"select switch from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))
        if up_r!=None and up_r!=[]:
            db.update_mysql(conn,"update app_scale_rule set switch=1 where marathon_name='{}' and app_id='{}' and scale_type='up'".format(marathon_name,app_id))
            result["msgup"]="up rule recover successfu."
            result["status"]="OK"
        else:
            result["msgup"]="{}:{} the up rule not setted.".format(marathon_name,app_id)
        down_r=db.select_mysql(conn,"select switch from app_scale_rule where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))
        if down_r!=None and down_r!=[]:
            db.update_mysql(conn,"update app_scale_rule set switch=1 where marathon_name='{}' and app_id='{}' and scale_type='down'".format(marathon_name,app_id))
            result["status"]="OK"
            result["msgdown"]="down rule recover successful"
        else:
            result["msgdown"]="{}:{} the down rule not setted.".format(marathon_name,app_id)
        return result
    except Exception as e:
        reusult["status"]="NOT OK"
        logging.debug(e)
        return result
        

        

@app.route('/retest',method=['GET','POST'])
def request_test():
    data=json.loads(request.body.read())
    #return json.dumps(data)
    return data

if __name__=="__main__":
    #print( app_info('20.26.25.148','test'))
    #app_list("20.26.25.147")
    #rule={"marathon_name":"marathon","app_id":"test2"}
    #rule_set(rule)
    #rule_update(rule)
    app.run(host='192.168.2.17',port=8888)

