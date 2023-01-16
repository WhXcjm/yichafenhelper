from lxml import etree
from sys import argv
import pandas as pd
import requests
import time
import utils
import tkinter.filedialog as filedia
from utils import log

dataFileLoc = ".\data.csv"
dataFp = 0
data = 0
session = requests.session()
Param_test = """//a[@class="weui-cell weui-cell_access"]/@href"""
test_ID = 0
homeUrlParam = "https://{sid}.yichafen.com"
testUrlParam = """https://{sid}.yichafen.com/public/checkcondition/sqcode/{sqcode}/htmlType/default.html"""
queryrespUrlParam="""https://{sid}.yichafen.com/public/queryresult.html"""
tbHeaderParam="""//td[@class='left_cell']/span/text()"""
tbContentParam="""//td[@class='right_cell']/text()"""
errorParam="""//p[@class="error"]/text()"""


if(len(argv) > 1):
	dataFileLoc = argv[-1]
ext = dataFileLoc.split('.')[-1]

dataFp = open(dataFileLoc, "r")
if(ext == "csv"):
	log("csv")
	data = pd.read_csv(dataFp, header=0, index_col=None, dtype=str)
elif(ext == "xlsx" or ext == "xls"):
	log("excel")
	data = pd.read_excel(dataFp, header=0, index_col=None, dtype=str)
else:
	raise Exception("Unknown extension of the database")
col = data.columns
outputData={}


for tup in data.itertuples():
	log('--------')
	dt = tup[1:]
	i = tup[0]
	postdata = {}
	try:
		sid=tup[1]
		# 爬取条目信息
		for i in range(1, len(col)):
			postdata[col[i]] = dt[i]
		headers = {'User-Agent': utils.get_random_useragent()}
		# log(f"headers:{headers}; postdata:{postdata}")
		homeUrl = homeUrlParam.format(sid=sid)
		resp = session.get(url=homeUrl, headers=headers)
		resp.encoding = 'utf8'
		tree = etree.HTML(resp.text)
		testcode = tree.xpath(Param_test)[test_ID].split('.')[0].split('/')[-1]

		# 爬取测试信息
		# log(postdata)
		testUrl = testUrlParam.format(sid=sid, sqcode=testcode)
		resp=session.post(testUrl,postdata,headers=headers).text
		tree=etree.HTML(resp)
		err=tree.xpath(errorParam)
		if(len(err)>0):
			raise Exception(err[0])
		# log(resp)
		log("////////////////////////////")
		
		headers["Referer"]=testUrl
		resp=session.get(queryrespUrlParam.format(sid=sid),headers=headers)
		tree=etree.HTML(resp.text)
		tbHeader=tree.xpath(tbHeaderParam)
		tbContent=tree.xpath(tbContentParam)
		log(tbHeader)
		log(tbContent)
		if(str(sid) not in outputData.keys()):
			outputData[str(sid)]=pd.DataFrame(columns=tbHeader)
		outputData[str(sid)].loc[outputData[str(sid)].shape[0]]=tbContent
	except Exception as e:
		log(f"//////\nError occurs on {postdata}.\nError info: {e}\n//////")
		# raise(e)
	time.sleep(0.5)
log(outputData)
filename=filedia.asksaveasfile(filetypes=[("表格文档(*.xlsx,*.xls)","xlsx,xls")],title=f"Save",initialdir=".",initialfile=f"output.xlsx")
Fp=open(filename.name,"wb")
writer=pd.ExcelWriter(Fp)
for (id,dat) in outputData.items():
	dat.to_excel(writer,sheet_name=id)
	writer.save()