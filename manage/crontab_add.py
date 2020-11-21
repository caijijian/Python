#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################
#此脚本实现读取xlsx表格并根据表格中的数据完成crontab的批量添加
#Author：zhangjian@lingrengame.com
#Time: 2020-11-21 12:06:00
#第三方模块支持：pandas numpy python-crontab
#############################################################
import time
import pandas as pd
import numpy as np
import re
from crontab import CronTab

#读取xlsx函数
def read_excel(filename):
	pd.set_option('display.max_columns',None)
	pd.set_option('display.width',5000)
	text_xls = np.array(pd.read_excel(filename))
	return text_xls

data_xls = read_excel('kaifu.xlsx')
data_lis = data_xls.tolist()
time_str = time.strftime('%d %m',time.localtime())
for i in data_lis:
	time_xls = str(i[0])
	sel_time = time.strptime(time_xls,'%Y-%m-%d %H:%M:%S')
	exec_time = time.strftime('%d %m',sel_time)
	gameid = int(i[4].split('=')[1])
	comment = str(i[4].split('=')[1])
	user_cron = CronTab(user=True)
	flag = False
	#判断当前crontab中是否存在相同comment的计划任务
	for cron in user_cron.crons:
		if comment in str(cron):
			flag = True
	if flag:
		continue
	job1_content = "/bin/bash /data/salt/scripts/reset.sh game{0}".format(gameid)
	job2_content = "/bin/bash /data/salt/scripts/outside_v1.sh {0}".format(gameid)
	job1 = user_cron.new(command=job1_content)
	job2 = user_cron.new(command=job2_content)
	job1.set_comment(comment)
	job2.set_comment(comment)
	job1_time = '00 04 {0} *'.format(exec_time)
	job2_time = '10 05 {0} *'.format(exec_time)
	job1.setall(job1_time)
	job2.setall(job2_time)
	job1.enable()
	job2.enable()
	user_cron.write()
