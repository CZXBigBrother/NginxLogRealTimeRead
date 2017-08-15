#!/usr/bin/env python
#coding:utf8
import re
import sys
import MySQLdb
import datetime
import time
#日志的位置
logfile=open("/var/log/nginx/access.log")
ipP = r"?P<ip>[\d.]*"
timeP = r"""?P<time>\[[^\[\]]*\]"""
requestP = r"""?P<request>\"[^\"]*\""""
statusP = r"?P<status>\d+"
bodyBytesSentP = r"?P<bodyByteSent>\d+"
referP = r"""?P<refer>\"[^\"]*\""""
userAgentP = r"""?P<userAgent>\"[^\"]*\""""
userSystems = re.compile(r'\([^\(\)]*\)')
userlius = re.compile(r'[^\)]*\"')
nginxLogPattern = re.compile(r"(%s)\ -\ -\ (%s)\ (%s)\ (%s)\ (%s)\ (%s)\ (%s)" %(ipP, timeP, requestP, statusP, bodyBytesSentP, referP, userAgentP), re.VERBOSE)

sqlinsert = "INSERT INTO NginxHistory (`n_ip`,`n_time`,`n_request`,`n_status`,`n_bodysize`,`n_refer`,`n_info`,`n_system`,`n_browser`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
sqlselectlast = "SELECT n_time from NginxHistory ORDER BY id DESC LIMIT 1"
def nginxlog():
    lastTime = '获取数据库最后一条'#MysqlHelper().fetchone(sqlselectlast,[])
    if lastTime != None:
        lastTime = lastTime[0]
        print u'最后一次访问:'+lastTime
    else:
        lastTime = '1971-01-01 00:00:00'
    lastTime = datetime.datetime.strptime(lastTime, '%Y-%m-%d %H:%M:%S')
    logs = []
    while True:
        line = logfile.readline()
        if not line:
            #插入数据库
            # MysqlHelper().inserts(sqlinsert, logs)
            break
        matchs = nginxLogPattern.match(line)
        if matchs != None:
            allGroup = matchs.groups()
            Time = allGroup[1]
            Time = Time.replace('T',' ')[1:-7]
            Time = datetime.datetime.strptime(Time, '%d/%b/%Y:%H:%M:%S')
            if lastTime < Time:
                Time = str(Time)
                ip = allGroup[0]
                request = allGroup[2]
                status = allGroup[3]
                bodyBytesSent = allGroup[4]
                refer = allGroup[5]
                userAgent = allGroup[6]
                if len(userAgent) > 20:
                    userinfo = userAgent.split(' ')
                    userkel =  userinfo[0]
                    try:
                        usersystem = userSystems.findall(userAgent)
                        usersystem = usersystem[0]
                        userliu = userlius.findall(userAgent)
                        value = [ip,Time,request[0:100],status,bodyBytesSent,refer[:100],userkel,usersystem,userliu[1]]
                    except IndexError:
                        userinfo = userAgent
                        value = [ip,Time,request[0:100],status,bodyBytesSent,refer[:100],userinfo,"",""]
                else:
                    useraa = userAgent
                    value = [ip,Time,request[0:100],status,bodyBytesSent,refer[:100],useraa,"",""]
                print value
                logs.append(value)


if __name__ == '__main__':
    while True:
        nginxlog()
        #30s读取一次
        time.sleep(30)
