from sys import argv
import pandas as pd

dataFileLoc=".\data.csv"
dataFp=0
data=0
if(len(argv)>1):
	dataFileLoc=argv[-1]
ext=dataFileLoc.split('.')[-1]
try:
	dataFp=open(dataFileLoc,"r")
	if(ext=="csv"):
		print("csv")
		data=pd.read_csv(dataFp,header=0,index_col=None,encoding="utf8")
	elif(ext=="xlsx" or ext=="xls"):
		print("excel")
		data=pd.read_excel(dataFp,header=0,index_col=None)
	else:
		raise Exception("Unknown extension of the database")
	print(data.columns)
except Exception as e:
	print(e)
	input("按回车键结束程序")
	exit(0)