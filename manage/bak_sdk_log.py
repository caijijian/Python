#!/usr/bin/env python
#-*- coding:utf8 -*-
# Power by Lawrence2020-11-26 14:48:25
import sys
import os
from datetime import *

def bak_sdk4(normal_log_time,apache_log_time):
    local_log_path = '/data/log_from_sdk4/'
    cos_path_4 = 'xy_sdk_apache_logbak_4/' 
    ip = '172.31.0.4'
    try:
        for pro in os.listdir(local_log_path):
            if pro == 'apache':
                os.system("scp {ip}:/data/logs/apache/*_{time}.log /data/log_from_sdk4/{pro_name}".format(ip=ip,time=apache_log_time,pro_name=pro+'/'))
            elif pro == 'log':
                os.system("scp {ip}:/data/logs/sdk/{name}-{time}.php /data/log_from_sdk4/{pro_name}".format(ip=ip,name=pro,time=normal_log_time,pro_name=pro+'/'))
            else:
                os.system("scp {ip}:/data/logs/sdk/{name}-{time}.log /data/log_from_sdk4/{pro_name}".format(ip=ip,name=pro,time=normal_log_time,pro_name=pro+'/'))
        os.system("/usr/local/bin/coscmd upload -r {0} {1}".format(local_log_path,cos_path_4))
        os.system("find %s -type f -exec rm -rf {} \;" % local_log_path)
    except Exception as e:
        print('Upload sdk4 log failed.meg: {0}'.format(str(e)))

def bak_sdk3(normal_log_time,apache_log_time):
    local_log_path = '/data/log_from_sdk3/'
    cos_path_3 = 'xy_sdk_apache_logbak_3/'
    ip = '172.31.0.3'
    try:
        for pro in os.listdir(local_log_path):
            if pro == 'apache':
                os.system("scp {ip}:/data/logs/apache/*_{time}.log /data/log_from_sdk3/{pro_name}".format(ip=ip,time=apache_log_time,pro_name=pro+'/'))
            elif pro == 'log':
                os.system("scp {ip}:/data/logs/sdk/{name}-{time}.php /data/log_from_sdk3/{pro_name}".format(ip=ip,name=pro,time=normal_log_time,pro_name=pro+'/'))
            else:
                os.system("scp {ip}:/data/logs/sdk/{name}-{time}.log /data/log_from_sdk3/{pro_name}".format(ip=ip,name=pro,time=normal_log_time,pro_name=pro+'/'))
        os.system("/usr/local/bin/coscmd upload -r {0} {1}".format(local_log_path,cos_path_3))
        os.system("find %s -type f -exec rm -rf {} \;" % local_log_path)
    except Exception as e:
        print('Upload sdk3 log failed.meg: {0}'.format(str(e)))


if __name__ == '__main__':
    yesterday = datetime.today()+timedelta(-1)
    normal_log_time = yesterday.strftime('%Y-%m-%d')
    apache_log_time = yesterday.strftime('%Y%m%d')
    bak_sdk4(normal_log_time,apache_log_time)
    bak_sdk3(normal_log_time,apache_log_time)
