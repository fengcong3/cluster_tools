#!/public/home/fengcong//anaconda2/envs/py3/bin/python
#encoding:utf-8


from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
from urllib.parse import unquote
import sys

def mail(jobid,scriptname,workdir,subcmd,maxmem,maxvmem,subtime,runtime,user,user_mail):
    my_sender='xxxxxxxxx@qq.com' 
    my_pass = 'xxxxxxxxxxxxx' 
    my_user=user 
    ret=True
    try:
        txt="你的jobid:" + jobid +"--"+scriptname+" 已经完成！！\r\n\r\n"+"Workdir: "+workdir+ "\r\nmaxmem = "+maxmem +"Kb\r\nmaxvmem = "+ maxvmem  +"Kb\r\n\r\nqsub cmd: "+subcmd+ "\r\nqsub time: "+subtime+"\r\nruntime: "+runtime
        msg=MIMEText(txt,'plain','utf-8')
        msg['From']=formataddr(["cluster_agis",my_sender])
        msg['To']=formataddr([my_user,user_mail])
        msg['Subject']="%s--已经完成"%(jobid)
        server=smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login(my_sender, my_pass)
        server.sendmail(my_sender,[user_mail,],msg.as_string())
        server.quit() # 关闭连接 
    except Exception:
        ret=False

    return ret

if __name__  == '__main__':
    #WSGIServer(myapp,bindAddress=('127.0.0.1',8008)).run()
    arl=sys.argv[0:]
    seconds =int(eval(arl[8]))
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    #jobid scriptname workdir subcmd maxmem ,maxvmem subtime runtime user user_mail
    mail(arl[1],arl[2],arl[3],arl[4],arl[5],arl[6],arl[7],"%d:%02d:%02d" % (h, m, s),arl[9],arl[10])
