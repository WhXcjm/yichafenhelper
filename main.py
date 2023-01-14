from sys import argv
import pandas as pd
import requests
import time
import utils
from lxml import etree

dataFileLoc=".\data.csv"
dataFp=0
data=0
sesson=requests.session()
param_test="""//a[@class="weui-cell weui-cell_access"]/@href"""
test_ID=0

if(len(argv)>1):
	dataFileLoc=argv[-1]
ext=dataFileLoc.split('.')[-1]
try:
	dataFp=open(dataFileLoc,"r")
	if(ext=="csv"):
		print("csv")
		data=pd.read_csv(dataFp,header=0,index_col=None,dtype=str)
	elif(ext=="xlsx" or ext=="xls"):
		print("excel")
		data=pd.read_excel(dataFp,header=0,index_col=None,dtype=str)
	else:
		raise Exception("Unknown extension of the database")
	col=data.columns
	for tup in data.itertuples():
		dt=tup[1:]
		i=tup[0]
		postdata={}
		for i in range(1,len(col)):
			postdata[col[i]]=dt[i]
		headers={'User-Agent':utils.get_random_useragent()}
		# print(f"headers:{headers}; postdata:{postdata}")
		homeurl=f"https://{tup[1]}.yichafen.com"
		resp=sesson.get(url=homeurl,headers=headers)
		resp.encoding='utf8'
		tree=etree.HTML(resp.text)
		test=homeurl+tree.xpath(param_test)[test_ID]
		print(testurl)
		break
		time.sleep(0.5)
except Exception as e:
	print(e)
	input("按回车键结束程序")
	raise(e)
	exit(0)