#!/usr/bin/env python
#-*- coding:utf8 -*-
###########################################################
#	此脚本用于释放$1实例中所有被合并的游戏服数据库
#	$1为想要清理的数据库实例IP或实例外网地址
#	且此脚本只适用于以腾讯云COS为远程存储的场景中
#	Power by ZJ 2021-01-03 12:01:49
###########################################################
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
import time
import MySQLdb
import salt.client as sc
import color as st

salt_master = "*-ops-opserver-*"
mysql_user = ""
mysql_pwd = ""
mysql_port = 3306
mysql_charset = "utf8"
bak_path = "/data/DBbackup/base_bakup/"
cos_base_path = "DBbackup-nx_base"

#获取pillar中被合掉的区服
def Get_Merged():
	merged_list = []
	local = sc.LocalClient()
	tgt_name = salt_master
	try:
		pillar = local.cmd(tgt_name,'pillar.items')
		if len(pillar) <= 0:
			print('{0}获取pillar失败{1}'.format(st.color['FG_RED'],st.color['END']))
			sys.exit(1)
		ret = pillar.values()[0]['slist']
		for i in ret:
			if len(ret[i]['merge_server']) != 0:
				merged_list.append(i)
		return merged_list

	except Exception as e:
		print("{0}{1}{2}".format(st.color['FG_RED'],e,st.color['END']))
		return False

#主函数
def main(host):
	try:
		delete_db_list = []
		merge_list = Get_Merged()
		conn = MySQLdb.connect(
			host = host,
			user = mysql_user,
			passwd = mysql_pwd,
			port = mysql_port,
			charset = mysql_charset
		)
		cur = conn.cursor()
		cur.execute("show databases like 'nx_base_%';")
		data = cur.fetchall()
		if len(data) <= 0:
			print('{0}{1} {2}该实例上没有base库,请确认该实例是否为角色库!{3}'.format(st.color['FG_YELLOW'],host,st.color['FG_RED'],st.color['END']))
			sys.exit(0)
		for dbs in data:
			for db in dbs:
				game_id = db.split('_')[2]
				game_str = str('game' + game_id)
				if game_str in merge_list:
					delete_db_list.append(db)
		if len(delete_db_list) <= 0:
			print('{0} {1} 该数据库实例上没有被合掉的base库,请再次确认操作的数据库实例对象!{2}'.format(st.color['FG_RED'],host,st.color['END']))
			sys.exit(0)
		for db_name in delete_db_list:
			confirm = raw_input('{0}此次操作的数据库为: {1}{2}{3} ,是否确认执行?(YES/NO){4}: '.format(st.color['FG_GREEN'],st.color['FG_BLUE'],db_name,st.color['FG_GREEN'],st.color['END']))
			if confirm == 'YES' or confirm == 'yes':
			#执行备份并上传至COS
				if not Operate_DB(host,db_name):
					print('{0}数据库备份上传操作失败哦,请检查!{1}'.format(st.color['FG_RED'],st.color['END']))
					sys.exit(1)
				cur.execute("drop database %s;" % db_name)
			else:
				print('{0}数据库: {1}{2} {3}取消执行{4}'.format(st.color['FG_GREEN'],st.color['FG_BLUE'],db_name,st.color['FG_RED'],st.color['END']))
				continue
		print("{0}数据库实例: {1}{2} {3}清理成功{4}".format(st.color['FG_GREEN'],st.color['FG_BLUE'],host,st.color['FG_GREEN'],st.color['END']))
		cur.close()
		conn.close()
		return True

	except Exception as e:
		print(e)
		return False

#数据库执行函数
def Operate_DB(host,db_name):
	date_time = time.strftime("%Y%m%d")
	sql_path = bak_path + db_name
	sql_name = db_name+'_'+date_time+'.sql.gz'
	try:
		if not os.path.exists(sql_path):
			os.makedirs(sql_path)	
		#备份
		os.system("mysqldump -h%s -u%s -p%s %s --no-create-db --set-gtid-purged=off --ignore-table=%s.dump_roles --ignore-table=%s.dump_guilds --single-transaction --default-character-set=utf8|gzip|pv > %s" % (host,mysql_user,mysql_pwd,db_name,db_name,db_name,sql_path+'/'+sql_name))
		print('{0}{1} {2}备份完成!{3}'.format(st.color['FG_BLUE'],db_name,st.color['FG_GREEN'],st.color['END']))
		#上传至COS,这里也会根据使用的云厂商不同而导致上传方式不同
		os.system("coscmd upload -r %s %s" % (sql_path,cos_base_path+'/'))
		print('{0}{1} {2}上传至cos完成!{3}'.format(st.color['FG_BLUE'],db_name,st.color['FG_GREEN'],st.color['END']))
		os.system("rm -rf %s" % sql_path+'/'+'*.sql.gz')
		print('{0}{1} {2}本地删除完成!{3}'.format(st.color['FG_BLUE'],db_name,st.color['FG_GREEN'],st.color['END']))
		return True
	except Exception as e:
		print("{0}数据库: {1}操作失败,详情: {2}{3}".format(st.color['FG_RED'],db_name,e,st.color['END']))
		return False

if __name__ == '__main__':
	main(sys.argv[1])
