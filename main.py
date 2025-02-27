from lxml import etree
from sys import argv
from numpy import nan
from PIL import Image
import pandas as pd
import requests
import time
import re
import utils
import tkinter.filedialog as filedia
from tkinter import messagebox as mb
from utils import log
import json
dataFileLoc = ".\\data.csv"
dataFp = 0
data = 0
session = requests.session()
Param_test = """//a[@class="weui-cell weui-cell_access"]/@href"""
Param_test_date = """//p[@style="font-size:14px;color:#999;"]/text()"""
test_ID = 0
homeUrlParam = "https://{sid}.yichafen.com"
testUrlParam = """https://{sid}.yichafen.com/qz/{testcode}?from_device=mobile"""
verifyimgUrlParam = """https://{sid}.yichafen.com/public/verify.html"""
queryUrlParam = """https://{sid}.yichafen.com/public/verifycondition/sqcode/{sqcode}/from_device/mobile.html"""
queryrespUrlParam = """https://{sid}.yichafen.com/public/queryresult/from_device/mobile.html"""
tbHeaderParam = """//td[@class='left_cell']"""
tbContentParam = """//td[@class='right_cell']"""
errorParam = """//p[@class="error"]/text()"""


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
outputData = {}


for tup in data.itertuples():
    log('--------')
    try:
        dt = tup[1:]
        i = tup[0]
        postdata = {}
        sid = tup[1]
        # 爬取条目信息
        personalTestID = test_ID
        for i in range(1, len(col)):
            if(col[i] == "test_ID"):
                personalTestID = dt[i]
            else:
                postdata[col[i]] = dt[i]
        headers = {'User-Agent': utils.get_random_android_useragent()}
        # log(f"headers:{headers}; postdata:{postdata}")
        homeUrl = homeUrlParam.format(sid=sid)
        resp = session.get(url=homeUrl, headers=headers)
        resp.encoding = 'utf8'
        tree_homepage = etree.HTML(resp.text)
        tidlst=utils.handle_str_number_range(personalTestID,True)
    except Exception as e:
        log(f"//////\nError occurs while checking {postdata}.\nError info: {e}\n//////")
        # raise(e)
    for tid in tidlst:
        try:
            testcode = tree_homepage.xpath(Param_test)[tid].split('.')[0].split('/')[-1]
            testdate = tree_homepage.xpath(Param_test_date)[tid]
            aid = "{sid}_{tid} ({tdate})".format(
                sid=sid, tid=tid, tdate=testdate)
            # 根据testcode爬取sqcode，让客户分析ver-img
            verify = None
            testUrl = testUrlParam.format(sid=sid, testcode=testcode)
            testUrlHtml = session.get(testUrl, headers=headers).text
            captcha_img = etree.HTML(testUrlHtml).xpath("//div[@id='jsPicVerifyBox']//img[@id='verifyimg']/@src")
            if captcha_img:
                captcha_url = captcha_img[0]
                if not captcha_url.startswith("http"):
                    captcha_url = verifyimgUrlParam.format(sid=sid)

                # 下载验证码图片
                captcha_resp = session.get(captcha_url, headers=headers)
                with open("captcha.jpg", "wb") as f:
                    f.write(captcha_resp.content)

                # 显示验证码图片
                img = Image.open("captcha.jpg")
                img.show()

                # 输入验证码
                captcha_code = input("请输入验证码: ")

                # 将验证码添加到postdata中
                postdata["verify"] = captcha_code
            else:
                print("验证码不存在，可以继续处理")
                if "verify" in postdata:
                    del postdata["verify"]

            # log(testUrlHtml)
            sqcode = ""
            pattern = r'\$.post\("/public/verifycondition/sqcode/(\w+)/from'
            match = re.search(pattern, testUrlHtml,re.S)
            if match:
                sqcode = match.group(1)
            else:
                raise Exception("Failed to extract sqcode")

            # log(sqcode)
            # 爬取测试信息
            # log(postdata)
            queryUrl= queryUrlParam.format(sid=sid, sqcode=sqcode)
            resp = session.post(queryUrl, data=postdata, headers=headers).text
            # log(resp)
            tree = etree.HTML(resp)
            err = tree.xpath(errorParam)
            if(len(err) > 0):
                raise Exception(err[0])
            # log(resp)
            log("////////////////////////////")

            headers["Referer"] = testUrl
            resp = session.get(queryrespUrlParam.format(sid=sid), headers=headers)
            tree = etree.HTML(resp.text)
            tbHeader = tree.xpath(tbHeaderParam)
            tbContent = tree.xpath(tbContentParam)
            for i in range(len(tbHeader)):
                if(tbHeader[i].text):
                    tbHeader[i]=tbHeader[i].text
                else:
                    tbHeader[i]=''.join(tbHeader[i].xpath(".//text()")).strip()
            for i in range(len(tbContent)):
                if(tbContent[i].text):
                    tbContent[i]=tbContent[i].text
                else:
                    tbContent[i]=nan
            log(tbHeader)
            log(len(tbHeader))
            log(tbContent)
            log(len(tbContent))
            if(str(aid) not in outputData.keys()):
                outputData[str(aid)] = pd.DataFrame(columns=tbHeader)
            outputData[str(aid)].loc[outputData[str(aid)].shape[0]] = tbContent
        except Exception as e:
            log(f"//////\nError occurs while checking {postdata}(aid={aid}).\nError info: {e}\n//////")
            # raise(e)
    time.sleep(0.5)
log(outputData)
while(True):
    try:
        filename = filedia.asksaveasfile(filetypes=[("Microsoft Excel文件", "*.xlsx"),("Microsoft Excel 97-2003 文件", "*.xls")], title=f"Save", initialdir=".", initialfile=f"output.xlsx")
        Fp = open(filename.name, "wb")
        writer = pd.ExcelWriter(Fp)
        for (id, dat) in outputData.items():
            dat.to_excel(writer, sheet_name=id)
            writer._save()
        writer.close()
        break
    except Exception as e:
        log(f"//////\nError occurs in saving procedure.\nError info: {e}\n//////")
        if(mb.askretrycancel("ERROR","储存过程出现错误。\nError Info: {}".format(str(e)))==False):
            break
