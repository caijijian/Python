#!/usr/bin/env python
#-*- coding:utf8 -*-
# Power by ZJ 2020-12-19 17:35:12

import json
import os
import subprocess
import json
from urlparse import parse_qs
from wsgiref.simple_server import make_server

def application(environ,start_response):
	status = '200 OK'
	response_headers = [('Content-Type','text/html')]
	start_response(status,response_headers)
	params = environ['QUERY_STRING']
	server_id = params.split('=')[1]
	if server_id is None or not server_id.isdigit():
		return 'Server_id is suppose to be a number!'
	cmd = '''salt -N game gen_server.players game runlist=['game{0}']|grep -v sr | grep -v welcome|sed "s/>//g"|tr "\n" " "'''.format(server_id)
	if int(server_id) > 999:
		cmd = '''salt -N center gen_cross.players center unlist=['center{0}']|grep -v sr | grep -v welcome | sed "s/>//g"|tr "\n" " "'''.format(server_id)
	process = os.popen(cmd)
	output = process.read()
	process.close()
	my_list = output.split(',')
	if len(my_list) > 2:
		online_count = my_list[1]
		online_str = ''.join(online_count)
		online_str = online_str.replace('online:','')
		online_int = int(online_str)
	dic = {"server_id": server_id, "online_count": online_int}
	return json.dumps(dic)


if __name__ == '__main__':
	httpd = make_server('127.0.0.1',80,application)
	print('Server on port 80...')
	httpd.serve_forever()
