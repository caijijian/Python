#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 先安装PyMySQL模块 pip install PyMySQL

# 忽略产生的警告是信息
import warnings
warnings.filterwarnings('ignore')

# pyMysql CPython>= 2.6 or >= 3.3
import pymysql
import os
import sys
import logging
import time
import urllib
import urllib2
import socket
import requests
import pycurl
import json
from settings import *
from StringIO import StringIO
from threading import Thread

def getFileSize(filePath, size=0):
    for root, dirs, files in os.walk(filePath):
        for f in files:
            size += os.path.getsize(os.path.join(root,f))
    return int(size)

#onealert报警
def onealert(eventype,content,priority,details):
    payload = {
        'app':sr_onealert_key,           # string, 必填，告警集成的应用KEY
        'host': wan_ip,
        'eventType':eventype,   # string, 必填，触发告警trigger，解决告警resolve
        'eventId':'123456',     # string, 必填，事件 ID ，告警压缩和关闭时用到
        'alarmContent':content, # string, 可选
        'priority':priority,           # int, 可选，告警级别；提醒 1，警告 2，严重 3
        'entityName':hostname,
        'details': {
            "details":details
        },
        'contexts': [
            {
                "type": "link",
                "text": "generatorURL",
                "href": "http://****/lr_jc/zabbix.php?action=dashboard.view"
            }
       ]
    }

    # sending post request and saving response as response object
    r = requests.post(url = onealert_url, data = json.dumps(payload))

    # extracting response text
    pastebin_url = r.text
    print("The pastebin URL is:%s"%pastebin_url)

def district_bakup(host):
    error_db_list = []
    try:
        if(not(os.path.exists(district_back_path))):
            os.makedirs(district_back_path)
        #获取一个数据库连接，注意如果是UTF-8类型的，需要制定数据库
        conn = pymysql.connect(
            host=host,            # 数据库地址
            user=mysql_user,                 # 数据库用户名
            passwd=mysql_pwd,               # 数据库密码
            db='mysql',            # 数据名
            port=mysql_port,                   # 数据库访问端口
            charset=mysql_charset               # 数据库编码格式
        )
        cur = conn.cursor()              # 获取一个游标
        cur.execute("show databases like 'nx_%'")    # 查询出所有数据库
        data = cur.fetchall()            # 查询出来，并赋值 data
        for db_names in data: 
            for db_name in db_names:
                if(db_name=='information_schema' or db_name=='performance_schema' or db_name=='mysql'):
                    continue
                if(not(os.path.exists(district_back_path+db_name))):
                    os.makedirs(district_back_path+db_name)
                db_before_size=getFileSize(district_back_path+db_name)
                path = district_back_path+db_name+"/"+new_date+".sql.gz"   # 数据库备份路径
                os.system("mysqldump -h%s -u%s -p%s %s --set-gtid-purged=off --single-transaction --default-character-set=utf8|gzip|pv  > %s" % (host, mysql_user, mysql_pwd, db_name, path))
                db_after_size=getFileSize(district_back_path+db_name)
                if db_after_size - db_before_size <= 0:
                    error_db_list.append(db_name)
                    continue
                old_time = time.strftime("%Y%m%d",time.gmtime(time.time()-out_time))
                #此方式针对亚马逊的S3对象存储
                #os.system("python /data/mysqldump/upload_file.py %s %s" % (path,db_name))
                #此方式针对阿里的OSS对象存储
                #os.system("/usr/local/bin/ossutil64 cp -rf %s %s" % (district_back_path,cos_dis_path))
                #此方式针对腾讯的COS对象存储
                #os.system("/usr/local/bin/coscmd upload -r %s %s" % (district_back_path,cos_dis_path))
                os.system("rm -f %s*.sql.gz" % (district_back_path+db_name+"/"))
    
        cur.close()                      # 关闭游标
        conn.close()                     # 释放数据库资源
        
    except Exception as e:
        print u"{r}账号库数据备份异常,错误信息:{e}".format(r=region_name, e=e)
        onealert('trigger',u'{r}账号库数据备份异常,错误信息:{e}'.format(r=region_name, e=e),1, region_name)
    if len(error_db_list) > 0:
        str_error_db = ','.join(str(d) for d in error_db_list)
        error_msg = u"{r}账号库实例有数据库备份失败,异常数据库:{d}".format(r=region_name, d=str_error_db)
        onealert('trigger', error_msg,1, region_name)
        return False
    return True

def base_bakup(host):
    error_db_list = []
    try:
        if(not(os.path.exists(base_back_path))):
            os.makedirs(base_back_path)
        #获取一个数据库连接，注意如果是UTF-8类型的，需要制定数据库
        conn = pymysql.connect(
            host=host,            # 数据库地址
            user=mysql_user,                 # 数据库用户名
            passwd=mysql_pwd,               # 数据库密码
            db='mysql',            # 数据名
            port=mysql_port,                   # 数据库访问端口
            charset=mysql_charset               # 数据库编码格式
        )
        cur = conn.cursor()              # 获取一个游标
        cur.execute("show databases like 'nx_%'")    # 查询出所有数据库
        data = cur.fetchall()            # 查询出来，并赋值 data
        for db_names in data: 
            for db_name in db_names:
                if(db_name=='information_schema' or db_name=='performance_schema' or db_name=='mysql'):
                    continue
                if(not(os.path.exists(base_back_path+db_name))):
                    os.makedirs(base_back_path+db_name)
                path = base_back_path+db_name+"/"+new_date+".sql.gz"   # 数据库备份路径
                before_size=getFileSize(base_back_path+db_name)
                os.system("mysqldump -h%s -u%s -p%s %s --no-create-db --set-gtid-purged=off --ignore-table=%s.dump_roles --ignore-table=%s.dump_guilds --single-transaction --default-character-set=utf8|gzip|pv  > %s" % (host, mysql_user, mysql_pwd, db_name,db_name,db_name, path))
                after_size=getFileSize(base_back_path+db_name)
                if after_size - before_size <= 0:
                    error_db_list.append(db_name)
                    continue
                old_time = time.strftime("%Y%m%d",time.gmtime(time.time()-out_time))
                #此方式针对亚马逊的S3对象存储
                #os.system("python /data/mysqldump/upload_file.py %s %s" % (path,db_name))
                #此方式针对阿里的OSS对象存储
                #os.system("/usr/local/bin/ossutil64 cp -rf %s %s" % (base_back_path,cos_base_path))
                #此方式针对腾讯的COS对象存储
                #os.system("/usr/local/bin/coscmd upload -r %s %s" % (base_back_path,cos_base_path))
                os.system("rm -f %s*.sql.gz" % (base_back_path+db_name+"/"))
    
        cur.close()                      # 关闭游标
        conn.close()                     # 释放数据库资源
        
    except Exception as e:
        print(u"{r}角色库数据备份异常,错误信息:{e}".format(r=region_name, e=e))
        onealert('trigger',u'{r}角色库数据备份异常,错误信息:{e}'.format(r=region_name, e=e),1, region_name)
    if len(error_db_list) > 0:
        str_error_db = ','.join(str(d) for d in error_db_list)
        error_msg = u"{r}角色库实例有数据库备份失败,异常数据库:{d}".format(r=region_name, d=str_error_db)
        onealert('trigger', error_msg,1, region_name)
        return False
    return  True

if __name__ == '__main__':
    Thread(target = base_bakup(mysql_base1_host)).start()
    Thread(target = district_bakup(mysql_district_host)).start()
