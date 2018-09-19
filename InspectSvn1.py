#!/usr/bin/sh
# -*- coding: utf-8 -*-
import os
import time, datetime
import re
import smtplib
from email.mime.multipart import MIMEMultipart  # 导入MIMEMultipart类
from email.mime.text import MIMEText
from email.header import Header
from email.mime.image import MIMEImage
import shutil
'''
Created on 2018-08-13

@author: linsheng
'''

commitdictTrunk = {}
commitdictTrunks = []
commitdictBrank = []
notMergerCommit = []
sendTime = 0
clearTime = 0


# 获取当前路径
def getCurrentPath():
    currentPath = os.getcwd();
    return currentPath;


# 获取当天时间
def getCurrentData():
    nowTime = datetime.datetime.now().strftime('%Y-%m-%d')  # 现在
    return nowTime


# 获取当天时间
def getCurrentDataClear():
    nowTime = datetime.datetime.now().strftime('%H:%M')  # 现在
    print nowTime
    return nowTime


# trunk获取当天提交
def getCurrentCommitTrunk(text):
    for line in text:
        if (line.count("|") >= 2):
            commitTime = line.split("|");
            id = commitTime[0].split("r")
            timeDate = commitTime[2].split("+")
            timeDate = "".join(timeDate[0])
            commitdictTrunk[id[1]] = commitTime[1], timeDate
            commitdictTrunks.append("".join(id[1]))


# brank获取当天提交
def getCurrentCommitBrank(text):
    for line in text:
        if (line.count("|") >= 2):
            continue
        else:
            mathcher = r'(\d{6})'
            rs = re.findall(mathcher, line)
            if (len(rs) == 0):
                continue
            else:
                commitdictBrank.append("".join(rs));


# 检查trunk当天提交log信息,并记录下当前提交的revision ID 信息
def InspectTrunk(currentPath, trunkUrl):
    currentDrive = currentPath.split(":")[0];
    trunkDrive = trunkUrl.split(":")[0];
    currentTime = getCurrentData();

    if (currentDrive == trunkDrive):
        print "Current and trunk belong to the same driver symbol"
        r = os.popen(" cd  %s  && svn log -r {%sT00:00:00}:{%sT23:00:00} -v" % (trunkUrl, currentTime, currentTime))
        text = r.readlines()
        getCurrentCommitTrunk(text);
        r.close()

    else:
        print "Trunk To start the update"
        r = os.popen(" %s: && cd  %s  && svn log -r {%sT00:00:00}:{%sT23:00:00} -v" % (
        trunkDrive, trunkUrl, currentTime, currentTime))
        text = r.readlines()
        getCurrentCommitTrunk(text);
        r.close()


# 用于统计brank分值当天提交的log信息
def InspectBrank(currentPath, brankUrl):
    currentDrive = currentPath.split(":")[0];
    brankDrive = brankUrl.split(":")[0];
    currentTime = getCurrentData();

    if (brankUrl == currentDrive):
        print "Current and brank Belong to the same drive symbol"
        r = os.popen(" cd  %s  && svn log -r {%sT00:00:00}:{%sT23:00:00} -v" % (brankUrl, currentTime, currentTime))
        text = r.readlines()
        getCurrentCommitBrank(text);
        r.close()
    else:
        print "Brank To start the update"
        r = os.popen(" %s: && cd  %s  && svn log -r {%sT00:00:00}:{%sT23:00:00} -v" % (
            brankDrive, brankUrl, currentTime, currentTime))
        text = r.readlines()
        getCurrentCommitBrank(text);
        r.close()


# 判断是否属于同一个盘符下面，用于更新trunk 和分值代码
def isSameDirectory(currentPath, trunkUrl, brankUrl):
    currentDrive = currentPath.split(":")[0];
    trunkDrive = trunkUrl.split(":")[0];
    brankDrive = brankUrl.split(":")[0];

    if (currentDrive == trunkDrive):
        print "Current and trunk belong to the same driver symbol"
        os.system(" cd  %s  && svn update" % (trunkUrl))
    else:
        print "Trunk To start the update"
        os.system(" %s: && cd  %s  && svn update" % (trunkDrive, trunkUrl))

    if (brankUrl == currentDrive):
        print "Current and brank Belong to the same drive symbol"
        os.system(" cd  %s  && svn update" % (brankUrl))
    else:
        print "Brank To start the update"
        os.system(" %s: && cd  %s  && svn update" % (brankDrive, brankUrl))


# 发送邮件
def sendEmail(key, valuess):
    mail_host = "smtp.gmail.com"  # 设置服务器
    mail_user = "hulinsheng@conew.com"  # 用户名
    mail_pass = "olzmfmlwqvhuhgpg"  # 口令

    # sender = 'hulinsheng@conew.com'
    receivers = ['hulinsheng@conew.com', "".join(valuess[0]).strip()]  # 定义邮件发件人

    msgRoot = MIMEMultipart('related')
    subject = 'SVN Merged'
    msgRoot['Subject'] = Header(subject, 'utf-8')
    message = MIMEText('嘿，小哥你浪了奥，这条记录没有merged到分支，快点merged这条 ' + key + " 到分支", 'plain', 'utf-8')
    msgRoot.attach(message)
    mail_msg = """
                    <br>
                    <br>
                    <br/>
                    <br/>
                    <br/>
                    <p><img src ='cid:image1'></p>
                    """
    msgText = MIMEText('<img src="cid:image1">', 'html', 'utf-8')
    msgRoot.attach(msgText)
    # 指定图片为当前目录
    fp = open('D:\\launcher\\hahhaha.jpg', 'rb')
    msgImage = MIMEImage(fp.read())
    # 定义图片 ID，在 HTML 文本中引用
    msgImage.add_header('Content-ID', '<image1>')
    # print msgImage
    msgRoot.attach(msgImage)
    fp.close()

    try:
        smtpObj = smtplib.SMTP_SSL()
        smtpObj.connect(mail_host, 465)  # 25 为 SMTP 端口号
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(mail_user, receivers, msgRoot.as_string())
        print "邮件发送成功"
    except smtplib.SMTPException, e:
        print "Error: 无法发送邮件" + str(e)

#首先将差异文件生成出来
def diffFile(key,currentPath, trunkUrl,keyposition):
    currentDrive = currentPath.split(":")[0];
    trunkDrive = trunkUrl.split(":")[0];
    if(keyposition == 0):
        keyposition = commitdictTrunks[1];
    elif (keyposition == 1):
        keyposition = commitdictTrunks[0];
    else:
        keyposition = commitdictTrunks[keyposition-1];
    if (currentDrive == trunkDrive):
        print "svn diff -r %s:%s >D:\\a.patch"
        r = os.popen(" cd  %s  && svn diff -r %s:%s >D:\\a.patch" % (trunkUrl, key, keyposition))
        r.readlines()
        r.close()

    else:
        print "%s: && cd  %s  && svn diff -r  %s:%s >D:\\a.patch"
        r = os.popen(" %s: && cd  %s  && svn diff -r  %s:%s >D:\\a.patch" % (trunkDrive, trunkUrl, key, keyposition))
        r.readlines()
        r.close()


#patchFile
def patchFile(currentPath, brankUrl):
    currentDrive = currentPath.split(":")[0];
    brankDrive = brankUrl.split(":")[0];

    if (brankUrl == currentDrive):
        print "svn patch D:\\a.patch"
        r = os.popen(" cd  %s  && svn patch D:\\a.patch && svn add */**/*  && svn ci !(config.php) -m='多语言提交'" % (brankUrl))
        r.readlines()
        r.close()
    else:
        print "%s: && cd  %s  && svn patch D:\\a.patch"
        r = os.popen(" %s: && cd  %s  && svn patch D:\\a.patch && svn add */**/* && svn ci !(config.php) -m='多语言提交'" % (
            brankDrive, brankUrl))
        r.readlines()
        r.close()

# 对比trunk和分支的提交,保存分值没有提交的
def ComparedTrunkAndBrank(currentPath, trunkUrl,brankUrl):
    for key in commitdictTrunk.keys():
        print key
        print commitdictBrank
        if "".join(key).strip() in commitdictBrank:
            print "Has been submitted"
        else:
            valuess = commitdictTrunk.get(key);
            commitTime = "".join(valuess[1]).strip();
            commitName = "".join(valuess[0]).strip();
            now = int(time.time())
            timeArray = time.strptime(commitTime, "%Y-%m-%d %H:%M:%S")
            timeStamp = int(time.mktime(timeArray))
            if (now - timeStamp >= 600 and (commitName != "zhuyanlin@cmcm.com" or commitName != "qiuying@cmcm.com")):  # 1800
                if ("".join(key).strip() in notMergerCommit):
                    if (now - sendTime >= 300):
                        print sendTime
                        sendEmail(key, valuess);
                        sendTime = int(time.time())
                        notMergerCommit.append("".join(key))
                else:
                    sendEmail(key, valuess);
                    sendTime = int(time.time())
                    print sendTime
            else:
                if(commitName != "qiuying@cmcm.com"):
                     keyposition = commitdictTrunks.index(key);
                     print keyposition
                     if (len(commitdictTrunks) >=2):
                        diffFile(key,currentPath, trunkUrl,keyposition);
                     if (os.path.exists("D:\\a.patch")):
                        patchFile(currentPath, brankUrl);
                        shutil.rmtree("D:\\a.patch")



    commitdictTrunk.clear();
    del commitdictBrank[:];
    if (getCurrentDataClear() == "23:58"):
        del notMergerCommit[:];


# 控制中心
def RunInspect(trunkUrl, brankUrl):
    currentPaths = getCurrentPath();

    isSameDirectory(currentPaths, trunkUrl, brankUrl);

    InspectTrunk(currentPaths, trunkUrl);

    InspectBrank(currentPaths, brankUrl);

    ComparedTrunkAndBrank(currentPaths, trunkUrl,brankUrl);


# main方法
if __name__ == '__main__':
    trunkUrl = "D:\\launcher\\cm_myandroid\\trunk\\dev_launcher\\trunk5.0\\";
    brankUrl = "D:\\launcher\\cml_5.44.x_0813\\";
    while True:
        RunInspect(trunkUrl, brankUrl);



