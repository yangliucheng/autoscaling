# -*- encoding:utf-8 -*-
# !/usr/bin/env python

"""
Author: "Hunter Sun"
 Date : "2016,09,09,9:10"
"""

import os
import pymysql
import threading
import time
import math
import requests
import datetime
import json
import data_driver_v2

# 获取marathon url 时候需要使用的mesos 信息
mesos_urls = os.environ.get("MESOS_URLS", "10.254.9.55:5050;10.254.9.57:5050;10.254.9.57:5050")
marathon_name = os.environ.get("MARATHON_NAME", "marathon")

# 数据库信息
db_user = os.environ.get('DB_USER', 'root')
db_pass = os.environ.get('DB_PASS', 'root123')
db_host = os.environ.get('DB_HOST', '10.254.9.55')
db_port = os.environ.get('DB_PORT', 3306)
db_name = os.environ.get('DB_NAME', 'machine')
config = {
    'user': db_user,
    'password': db_pass,
    'host': db_host,
    'port': db_port,
    'database': db_name,
    'charset': 'utf8'}


# global scale_rule
# scale_rule = []
# scale_rule = []

# scale_time = {}


def timer():
    """
    :this time is collect period.get from the db.
    """
    print("Successfully completed a cycle, sleeping for 5 seconds ...")
    time.sleep(5)
    return


def getinfo(db, marathon_name, app_id):
    now_info = data_driver_v2.data_driver(db, marathon_name, app_id)
    print("DEBUG====getinfo:", now_info)
    now_quota_info = {}
    try:
        if now_info['status'] == 0:
            now_quota_info['cpu'] = now_info['cpu']
            now_quota_info['memory'] = now_info['mem']
            now_quota_info['ha_queue'] = now_info['haproxy_backend_current_queue']
            now_instances = now_info['app_task_num']
        else:
            now_quota_info = {}
            now_instances = 0
        return now_quota_info, now_instances
    except Exception as e:
        print(e)


def scale_task(marathon, appid, thresh_hold, scale_type, scale_instances):
    target_instances = 0
    # print("DEBUG==before====scale_task{},{},{}".format(thresh_hold, scale_type, scale_instances))
    auth = ('dcosadmin', 'zjdcos01')
    data = {}
    if scale_type == 'scale_down':
        if scale_instances < thresh_hold:
            target_instances = thresh_hold
        else:
            target_instances = scale_instances
        data = {'instances': target_instances}
    if scale_type == 'scale_up':
        if scale_instances > thresh_hold:
            target_instances = thresh_hold
        else:
            target_instances = scale_instances
        data = {'instances': target_instances}
    json_data = json.dumps(data)
    # print("DEBUG======scale-task===", target_instances)
    print("json_data: ", json_data)
    headers = {'Content-type': 'application/json'}
    # response = requests.put(marathon_url + '/v2/apps/' + appid, json_data, headers=headers)
    try:
        response = requests.put(marathon + '/v2/apps/' + appid, json_data, headers=headers, auth=auth)
    except:
        response = requests.put(marathon + '/v2/apps/' + appid, json_data, headers=headers)
    print ('Scale_app return status code =', response.status_code)


def scale(marathon, appid, rule):
    """
    rule: {'marathon_name': u'20.26.25.148',
    'scale_down': {'switch': 1, 'cold_time': 4, 'continue_period': 3, 'thread': 1, 'memory': 1, 'ha_queue': 0,
    'collect_period': 5, 'cpu': 0, u'cpu_min_threshold': Decimal('0.3'),
    u'thread_min_threshold': Decimal('2.0')}, 'app_id': u'tcp.healthcheck', 'scale_type': u'down'}
    :param marathon:
    :param appid:
    :param rule:
    :return:
    """
    # print("debug==========scale=====scale_rule:", scale_rule)
    # print("marathon  scale_type  app_id", marathon, rule['scale_type'], appid)
    # for L in scale_rule:
    #     # 规则发生变化，进行更新
    #     if marathon == L['marathon_name'] and rule['scale_type'] == L['scale_type'] and appid == L['app_id']:
    #         rule = L
    #     # 规则删除(up or down)
    #     elif rule['scale_type'] not in L:
    #         rule = {}
    # print("DEBUG======scale ===rule:", rule)
    quotas = ['cpu', 'memory', 'thread', 'ha_queue']
    if (marathon + appid + rule['scale_type']) not in scale_time:
        scale_time[marathon + appid + rule['scale_type']] = time.time()
    if 'scale_up' in rule:  # 扩容条件
        # print("In the scale_up: rule:", rule)
        scale_up = 0
        now_tasks = 0
        scale_quotas = []
        now_quota_info = {}
        for quota in quotas:
            if rule['scale_up'][quota]:
                scale_quotas.append(quota)
        for rd in range(rule['scale_up']['continue_period']):
            now_quota_info_temp = {}
            task_temp = 0
            while not now_quota_info_temp and not task_temp:  # 保证能够获取到数据
                marathon_ip = marathon.split(":")[1].strip('/')
                print("the app {} 第{}次检查扩容,time:{}".format(appid, rd + 1,datetime.datetime.now()))
                now_quota_info_temp, task_temp = getinfo("prometheus", marathon_ip, appid)
            now_quota_info, now_tasks = now_quota_info_temp, task_temp
            temp = 0
            for scale_quota in scale_quotas:
                if now_quota_info[scale_quota] > rule['scale_up'][scale_quota + '_max_threshold']:
                    temp += 1
                else:
                    temp -= 1
            if temp >= 0:
                scale_up += 1
                conn = pymysql.connect(**config)
                cur = conn.cursor()
                count_status = '{}/{}'.format(rd + 1, rule['scale_up']['continue_period'])
                if rd < 2:
                    cur.execute(
                        "insert into scale_log(marathon_name,app_id,time,count_status,event) values('{}','{}',"
                        "'{}','{}','{}')".format(marathon, appid, str(datetime.datetime.now()), count_status, 'NO'))
                    conn.commit()
                    cur.close()
                    conn.close()
                    print("===========这是{}第{}次超过指标===========".format(appid, (rd + 1)))
            time.sleep(rule['scale_up']['collect_period'])
        end_time = time.time()
        # 如果次数超过3次,且扩缩容时间间隔大于指定cold_time 则执行缩容策略
        if scale_up == rule['scale_up']['continue_period'] and int(
                math.ceil(end_time - scale_time[marathon + appid + rule['scale_type']])) > rule['scale_up']['cold_time']:
            scale_instances = now_tasks + rule['scale_up']['per_auto_scale']
            scale_thresh = rule['scale_up']['scale_threshold']
            scale_time[marathon + appid + rule['scale_type']] = time.time()
            conn = pymysql.connect(**config)
            cur = conn.cursor()
            cur.execute(
                "insert into scale_log(marathon_name,app_id,time,count_status,event) values('{}','{}','{}','{}','{}')".format(
                    marathon, appid, str(datetime.datetime.now()), count_status, "YES"))
            conn.commit()
            cur.close()
            conn.close()
            print("============这是{}第{}次超过指标=进入弹性扩缩函数============".format(appid, 3))
            scale_task(marathon, appid, scale_thresh, 'scale_up', scale_instances)
            print("=============The app: {} needs to Scale up!time: {}".format(appid,
                                                                               scale_time[marathon + appid + rule[
                                                                                   'scale_type']]))
        else:
            print("=============The app: {} doesn't need to Scale up!".format(appid))

    elif 'scale_down' in rule:  # 缩容条件
        scale_down = 0
        now_tasks = 0
        scale_quotas = []
        now_quota_info = {}
        # print("DEBUG =========scale==========rule:%s" % rule)
        for quota in quotas:  # 从规则表里取出选中的指标进行比较判断
            if rule['scale_down'][quota]:  # 判断指标是否存在于规则表中
                scale_quotas.append(quota)
        # print("DEBUG========scale========scale quotas: %s,%s" % (appid, scale_quotas))
        for rd in range(rule['scale_down']['continue_period']):  # 遍历次数，持续周期
            # print("DEBUG=================scale:", scale_quotas)
            now_quota_info_temp = {}
            task_temp = 0
            while not now_quota_info_temp and not task_temp:  # 保证能够获取到数据
                print("the app {} 第{}次检查缩容,time:{}".format(appid, rd + 1, datetime.datetime.now()))
                marathon_ip = marathon.split(":")[1].strip('/')
                now_quota_info_temp, task_temp = getinfo("prometheus", marathon_ip, appid)
            now_quota_info, now_tasks = now_quota_info_temp, task_temp
            temp = 0
            for scale_quota in scale_quotas:
                if now_quota_info[scale_quota] < rule['scale_down'][scale_quota + '_min_threshold']:
                    temp += 1
                else:
                    temp -= 1
            if temp == len(scale_quotas):
                scale_down += 1
                conn = pymysql.connect(**config)
                cur = conn.cursor()
                count_status = '{}/{}'.format(rd + 1, rule['scale_down']['continue_period'])
                if rd < 2:
                    cur.execute(
                        "insert into scale_log(marathon_name,app_id,time,count_status,event) values('{}','{}','{}','{}','{}')".format(
                            marathon, appid, str(datetime.datetime.now()), count_status, 'NO'))
                    conn.commit()
                    cur.close()
                    conn.close()
                    print("这是 {}第 {} 次低于指标".format(appid, (rd + 1)))
            time.sleep(rule['scale_down']['collect_period'])
        end_time = time.time()
        print("last==scale_time===========%s " % scale_time[marathon + appid + rule['scale_type']])
        # 如果次数超过3次,且扩缩容时间间隔大于指定cold_time 则执行缩容策略
        if scale_down == rule['scale_down']['continue_period'] and int(
                math.ceil(end_time - scale_time[marathon + appid + rule['scale_type']])) > rule['scale_down']['cold_time']:
            scale_instances = now_tasks - rule['scale_down']['per_auto_scale']
            scale_thresh = rule['scale_down']['scale_threshold']
            scale_time[marathon + appid + rule['scale_type']] = time.time()
            conn = pymysql.connect(**config)
            cur = conn.cursor()
            cur.execute(
                "insert into scale_log(marathon_name,app_id,time,count_status,event) values('{}','{}','{}','{}','{}')".format(
                    marathon, appid, str(datetime.datetime.now()), count_status, 'Yes'))
            conn.commit()
            cur.close()
            conn.close()
            print("这是 {}第 {} 次低于指标".format(appid, 3))
            scale_task(marathon, appid, scale_thresh, 'scale_down', scale_instances)
            print("The app: {} needs to Scale Down!!! time: {}\n".format(appid, scale_time[
                marathon + appid + rule['scale_type']]))
        else:
            print("The app: {} doesn't need to Scale Down!!!\n".format(appid))
    else:
        print("The app:{} has no rule!".format(appid))
    time.sleep(2)


def test():
    time.sleep(5)
    global scale_time
    scale_time = {}
    while True:
        scale_threads = []
        # print("DEBUG===========test:=====scale-rule:", scale_rule)
        for rule in scale_rule:
            marathon_name = rule['marathon_name']
            app_id = rule['app_id']
            # print("DEBUG===========test:=====rule:", rule)
            scale_thread = threading.Thread(target=scale, args=(marathon_name, app_id, rule))
            scale_threads.append(scale_thread)
        for t in scale_threads:
            try:
                t.start()
            except Exception as e:
                print("ERROR: ", e)
        time.sleep(10)


def get_marathon_url_by_mesos(mesos_urls, marathon_name):
    """
    :param mesos_urls:
    :param marathon_name:
    :return: http://20.26.25.148:8080
    """
    t_e = 0  # 检查异常次数
    t_f = 0  # 检查frameworks为空次数
    t_m = 0  # 检查marathon name为空次数
    t_resp = 0  # 检查响应非200次数
    mesos_url_list = mesos_urls.split(";")
    headers = {"Content-type": "application/json"}
    for mesos_url in mesos_url_list:
        req_url = "http://" + mesos_url + "/master/frameworks"
        # print ("request url is : " + req_url)
        try:
            resp = requests.get(req_url, headers=headers)
            if resp.status_code != 200:
                # print ("request url :" + req_url + " return response code : " + resp.status_code)
                t_resp = t_resp + 1
                if t_resp >= len(mesos_url_list):
                    return str(t_resp) + " times reveive code non-statusOk!"
                    # 请求所有mesos url 都返回了非200状态码
            result = json.loads(resp.text)
            if result["frameworks"] != []:
                for framework in result["frameworks"]:
                    if framework["name"] == marathon_name:
                        return framework["webui_url"]
                        # 只要有一台mesos master 返回了framework webui_url就算成功返回
                    else:
                        t_m = t_m + 1
                        if t_m >= len(result["frameworks"]):
                            return "mesos : " + req_url + " don't have frameworks name: " + marathon_name
                            # mesos url中没有名字为marathon_name的框架
            else:
                t_f = t_f + 1
                if t_f >= len(mesos_url_list):
                    return str(t_f) + " times null frameworks"
                    # 请求所有mesos url 都没有返回任何框架
        except Exception as e:
            t_e = t_e + 1
            print(Exception, " : ", e)
            if t_e >= len(mesos_url_list):
                return t_e
                # 请求所有mesos url都跑出了异常


def dcos_init():
    while True:
        global scale_rule
        scale_rule = []
        conn = pymysql.connect(**config)
        cur = conn.cursor()
        try:
            cur.execute("select * from app_scale_rule where switch=1")
            rows = cur.fetchall()
            for row in rows:
                marathon_name = row[0]
                marathon_url = get_marathon_url_by_mesos(mesos_urls, marathon_name)
                temp = {
                    'marathon_name': marathon_url,
                    'app_id': row[1],
                    'scale_type': row[2],
                }
                if temp['scale_type'] == 'up':
                    scale_up = {
                        'scale_threshold': row[3],
                        'per_auto_scale': row[4],
                        'memory': row[5],
                        'cpu': row[6],
                        'thread': row[7],
                        'ha_queue': row[8],
                        'switch': row[9],
                        'cold_time': row[10],
                        'collect_period': row[11],
                        'continue_period': row[12],
                    }
                    try:
                        cur.execute(
                            "select * from quota_info where marathon_name=%s AND app_id=%s",
                            (row[0], temp['app_id']))
                        rows = cur.fetchall()
                        for row in rows:
                            quota = row[2]
                            quota_max_threshold = quota + "_max_threshold"
                            scale_up[quota_max_threshold] = row[3]
                    except Exception as e:
                        print (e)
                    temp['scale_up'] = scale_up
                if temp['scale_type'] == 'down':
                    scale_down = {
                        'scale_threshold': row[3],
                        'per_auto_scale': row[4],
                        'memory': row[5],
                        'cpu': row[6],
                        'thread': row[7],
                        'ha_queue': row[8],
                        'switch': row[9],
                        'cold_time': row[10],
                        'collect_period': row[11],
                        'continue_period': row[12],
                    }
                    try:
                        cur.execute(
                            "select * from quota_info where marathon_name=%s AND app_id=%s",
                            (row[0], temp['app_id']))
                        rows = cur.fetchall()
                        for row in rows:
                            quota = row[2]
                            quota_min_threshold = quota + "_min_threshold"
                            scale_down[quota_min_threshold] = row[4]
                    except Exception as e:
                        print (e)
                    temp['scale_down'] = scale_down
                scale_rule.append(temp)
        except Exception as e:
            print(e)
        print("DEBUG-------dcos_init========scale_rule: %s " % scale_rule)
        cur.close()
        conn.close()
        time.sleep(5)


if __name__ == '__main__':
    threads = []
    t1 = threading.Thread(target=dcos_init)
    threads.append(t1)
    t2 = threading.Thread(target=test)
    threads.append(t2)
    for i in threads:
        try:
            i.start()
        except Exception as e:
            print(e)
