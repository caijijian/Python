#!/usr/bin/env python
#-*- coding:utf8 -*-
# Power by Lawrence2020-12-07 15:31:30

import sys
import re
import subprocess
import json



def return_lister_game_info(start_id,stop_id,cmd):
	try:
		lister_info = subprocess.run(cmd,shell=True,stdout=subprocess.PIPE)
		lister_info = lister_info.stdout.decode()
	except Exception as e:
		print(e)
		sys.exit()
	row_data = {}
	re_lister = re.compile('ready.*?\((.*?)\).*?\[(.*?)\]',re.S)
	lister_info_set = re_lister.findall(lister_info)
	for lister_info in lister_info_set:
		lister_ip = lister_info[0]
		game_list = re.sub('[" " | {|}]','',lister_info[1])
		for gameinfo in game_list.replace('\n,\n',';').replace('\n','').split(';'):
			for id in range(start_id,stop_id):
				if 'ServerId:%s' % id not in gameinfo:
					continue
				if lister_ip in row_data:
					row_data[lister_ip].append(gameinfo)
				else:
					row_data[lister_ip] = [gameinfo]
	return row_data

def return_app_game_info(start_id,stop_id,cmd):
	try:
		app_info = subprocess.run(cmd,shell=True,stdout=subprocess.PIPE)
		app_info = app_info.stdout.decode()
	except Exception as e:
		print(e)
		sys.exit()
	raw_data = {}
	re_appList = re.compile('read.*?\((.*?)\).*?welcome\s+(\w+\s\d+).*?({.*?index.*?times:.*?})',re.S)
	appList = re_appList.findall(app_info)
	for query_set in appList:
		appip = query_set[0]
		appid = query_set[1]
		game_list = re.sub('[\"\{\}\r" "]','',query_set[2])
		for gameinfo in game_list.strip().split('\n'):
			for id in range(start_id,stop_id):
				if 'server:%s' % id not in gameinfo:
					continue
				if appid + '(' + appid + ')' in raw_data:
					raw_data[appid + '(' + appid + ')'].append(gameinfo)
				else:
					raw_data[appid + '(' + appid + ')'] = [gameinfo]
	return raw_data



def res_data(start_id,stop_id,app_set):
    data = {}
    app_cmd = 'salt-run saier.{}_info'
    for app in app_set:
        print('\033[0;32;40mget %s info\033[0m' % app)
        if app == 'lister':
            app_data = return_lister_game_info(start_id,stop_id,app_cmd.format(app))
        else:
            app_data = return_app_game_info(start_id,stop_id,app_cmd.format(app))
			data[app] = app_data
    return data


if __name__ == '__main__':
	app_set = ['lister','mirror','global','charge','manage','center','sns']
	start_id = int(sys.argv[1])
	stop_id = (int(sys.argv[2]) + 1)
	data = res_data(start_id,stop_id,app_set)
	print(json.dumps(data,indent=5))
