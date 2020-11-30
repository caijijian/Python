#!/usr/bin/env python
# -*- coding:utf-8 -*-
#########################################################################
#此脚本实现本地文件上传至aws对象存储s3的功能,在运行之前需要先进行s3的认证
#Author：zhangjian@lingrengame.com
#Time: 2020-11-21 16:36:00
#第三方摸快：boto3
########################################################################
import logging
import commands
import boto3
import sys
import os
import re
from botocore.exceptions import ClientError
bucket = 'sr-kr-bak'  ##桶名

def upload_file(file_name, bucket, object_name=None): ##上传文件的函数
    s3_client = boto3.client('s3')
    if object_name is None:
	object_name = file_name
    try:
	response = s3_client.upload_file(file_name, bucket , object_name)
    except ClientError as e:
	logging.error(e)
	return False
    return True

s3 = boto3.client('s3')
file_path = sys.argv[1]       
file_type = sys.argv[2]
file_name =commands.getstatusoutput("ls '%s' | awk -F / '{print $NF}' "%(file_path))  ##截取文件名
which_base = re.match('nx_base',file_type)
which_center = re.match('nx_center',file_type)

if which_base or which_center:    ##如果是游戏服和跨服
   key_name= 'DBbackup-nx_base-kr/'+file_type+'/'+file_name[1]   ##拼接成的文件上传路径和 备份名称(文件名)
   with open(file_path, 'rb') as f:
       s3.upload_fileobj(f, bucket, key_name) 
else:                            ##不是游戏服和跨服的路径
   key_name= 'DBbackup-nx_district-kr/'+file_type+'/'+file_name[1]   ##拼接成的文件上传路径和 备份名称(文件名)
   with open(file_path, 'rb') as f:
       s3.upload_fileobj(f, bucket, key_name) 
