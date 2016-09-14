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

db_user = os.environ.get('DB_USER', 'root')
db_pass = os.environ.get('DB_PASS', 'root123')
db_host = os.environ.get('DB_HOST', 'localhost')
db_port = os.environ.get('DB_PORT', 3306)
db_name = os.environ.get('DB_NAME', 'machine')
config = {
    'user': db_user,
    'password': db_pass,
    'host': db_host,
    'port': db_port,
    'database': db_name,
    'charset': 'utf8'}


class DB(object):
    def __init__(self):
        db_user = os.environ.get('DB_USER', 'root')
        db_pass = os.environ.get('DB_PASS', 'root123')
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', 3306)
        db_name = os.environ.get('DB_NAME', 'machine')
        self.config = {
            'user': db_user,
            'password': db_pass,
            'host': db_host,
            'port': db_port,
            'database': db_name,
            'charset': 'utf8'}

    def get_db(self):
        pass

    def show_db(self, marathon_name=None, app_id=None):
        if not marathon_name and not app_id:
            try:
                conn = pymysql.connect(**self.config)
                cur = conn.cursor()
                cur.execute('select * from app_scale_rule')
                rows = cur.fetchall()
                for row in rows:
                    print("rows:", row[0])
                    return row[0]
                cur.close()
                conn.close()
            except pymysql.Error as e:
                print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        else:
            try:
                conn = pymysql.connect(**self.config)
                cur = conn.cursor()
                cur.execute('select * from app_scale_rule where marathon_name = %s and app_id = %s',
                            (str(marathon_name), str(app_id)))
                rows = cur.fetchall()
                for row in rows:
                    print("rows:", row[0])
                    return row
                cur.close()
                conn.close()
            except pymysql.Error as e:
                print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        pass

    def insert_db(self, ):
        pass

    def update_db(self, ):
        pass

    def delete_db(self, ):
        pass


scale_rule = []
scale_time = {}


def timer():
    """
    :this time is collect period.get from the db.
    """
    print("Successfully completed a cycle, sleeping for 5 seconds ...")
    time.sleep(5)
    return


def getinfo():
    now_info = {'cpu': 1, 'memory': 1, 'thread': 11, 'app_task_num': 1}
    now_quota_info = {}
    now_quota_info['cpu'] = now_info['cpu']
    now_quota_info['memory'] = now_info['memory']
    now_quota_info['thread'] = now_info['thread']
    now_instances = now_info['app_task_num']
    return now_quota_info, now_instances


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
    while True:
        quotas = ['cpu', 'memory', 'thread', 'ha_queue']
        # print("DEBUG==========scale==========rule: %s" % rule)
        if ('marathon' + 'appid') not in scale_time:
            scale_time['marathon' + 'appid'] = time.time()
        # print("DEBUG==========scale==========appid: %s" % appid)
        if 'scale_up' in rule:  # 扩容条件
            scale_up = 0
            now_task = 0
            scale_quotas = []
            for quota in quotas:
                if rule['scale_up'][quota]:
                    scale_quotas.append(quota)
            for rd in range(rule['scale_up']['continue_period']):
                now_quota_info, now_tasks_number = getinfo()
                temp = 0
                for scale_quota in scale_quotas:
                    if now_quota_info[scale_quota] > rule['scale_up'][scale_quota + '_max_threshold']:
                        temp += 1
                    else:
                        temp -= 1
                if temp >= 0:
                    scale_up += 1
                time.sleep(rule['scale_up']['collect_period'])
            end_time = time.time()
            # 如果次数超过3次,且扩缩容时间间隔大于指定cold_time 则执行缩容策略
            if scale_up == rule['scale_up']['continue_period'] and int(
                    math.ceil(end_time - scale_time['marathon' + 'appid'])) > rule['scale_up']['cold_time']:
                scale_instances = now_task + rule
                scale_time['marathon' + 'appid'] = time.time()
                print("The app: {} needs to Scale up!!! time: {}".format(appid, scale_time['marathon' + 'appid']))
            else:
                print("The app: {} doesn't need to Scale up!".format(appid))

        if 'scale_down' in rule:  # 缩容条件
            scale_down = 0
            now_task = 0
            scale_quotas = []
            for quota in quotas:
                if rule['scale_down'][quota]:
                    scale_quotas.append(quota)
            print("DEBUG========scale========scale quotas: %s" % scale_quotas)
            for rd in range(rule['scale_down']['continue_period']):
                now_quota_info, now_tasks_number = getinfo()
                # 判断逻辑
                temp = 0
                for scale_quota in scale_quotas:
                    if now_quota_info[scale_quota] > rule['scale_down'][scale_quota + '_min_threshold']:
                        temp += 1
                    else:
                        temp -= 1
                if temp == len(scale_quotas):
                    scale_down += 1
                time.sleep(rule['scale_down']['collect_period'])
            end_time = time.time()
            print("last==scale_time===========%s " % scale_time['marathon' + 'appid'])
            # 如果次数超过3次,且扩缩容时间间隔大于指定cold_time 则执行缩容策略
            if scale_down == rule['scale_down']['continue_period'] and int(
                    math.ceil(end_time - scale_time['marathon' + 'appid'])) > rule['scale_down']['cold_time']:
                scale_instances = now_task + rule['scale_down']['per_auto_scale']
                scale_time['marathon' + 'appid'] = time.time()
                print("The app: {} needs to Scale Down!!! time: {}\n".format(appid, scale_time['marathon' + 'appid']))
            else:
                print("The app: {} doesn't need to Scale Down!!!\n".format(appid))
        time.sleep(2)


def test():
    time.sleep(2)
    scale_threads = []
    global scale_time
    scale_time = {}
    for rule in scale_rule:
        marathon_name = rule['marathon_name']
        app_id = rule['app_id']
        scale_thread = threading.Thread(target=scale, args=(marathon_name, app_id, rule))
        scale_threads.append(scale_thread)
    for t in scale_threads:
        try:
            t.start()
        except Exception as e:
            print("ERROR: ", e)


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
                temp = {
                    'marathon_name': row[0],
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
                            (temp['marathon_name'], temp['app_id']))
                        rows = cur.fetchall()
                        for row in rows:
                            quota = row[2]
                            quota_max_threshold = quota + "_max_threshold"
                            scale_up[quota_max_threshold] = row[3]
                    except Exception as e:
                        print (e)
                    temp['scale_up'] = scale_up
                elif temp['scale_type'] == 'down':
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
                            (temp['marathon_name'], temp['app_id']))
                        rows = cur.fetchall()
                        for row in rows:
                            quota = row[2]
                            quota_min_threshold = quota + "_min_threshold"
                            scale_down[quota_min_threshold] = row[4]
                    except Exception as e:
                        print (e)
                    temp['scale_down'] = scale_down
                scale_rule.append(temp)
            # print("DEBUG==========dcos——init===scale_rule: %s" % scale_rule)
        except Exception as e:
            print(e)
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
