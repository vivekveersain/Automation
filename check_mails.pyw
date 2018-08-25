from requests import Session
from re import findall
from time import time,sleep
from requests.auth import HTTPBasicAuth
from TTS import rachel
from popup import notify
from tkinter import Tk,Label,StringVar
import random

auth = HTTPBasicAuth('vivek.jhajjar@gmail.com', 'hurtkuvkbkdbnpwr')
url='https://mail.google.com/mail/feed/atom'

start_tag={'name':'author><name','email':'/name><email','summary':'summary',"title":"title"}
end_tag={'name':'name><email','email':'email></author','summary':'summary',"title":"title"}

def parser(tag,text):
    return findall('<%s>(.*?)</%s>'%(start_tag[tag],end_tag[tag]),text)[0]

def speak(x):
    if x%10==1:
        if x%100==11: return str(x)+'th'
        else:return str(x)+'st'
    elif x%10==2:
        if x%100==12: return str(x)+'th'
        else:return str(x)+'nd'
    elif x%10==3:
        if x%100==13: return str(x)+'th'
        else:return str(x)+'rd'
    else:return str(x)+'th'

def display(text,speech):
    message.set(text)
    root.geometry('-%d-%d' % (0,40))
    root.update()
    rachel(speech)

sleep(30)
old_emails=0
timer=time()
rachel("Checking for new emails.")
with Session() as s:
    while True:
        try:
            r=s.post(url=url, auth=auth).text
            unread=int(findall('<fullcount>(\d+)</fullcount>',r)[0])
            new_emails=unread-old_emails
            if new_emails>0:
                if new_emails==1: msg="You have 1 NEW email        "
                else: msg="You have %d NEW emails       " % (new_emails)
                root=Tk()
                root.overrideredirect(True)
                root.wm_attributes("-topmost", True)
                message,title = StringVar(),StringVar()
                Label(root,textvariable=message,justify='left',font=("Times", 12)).pack()
                display("Gmail!\n\n%s"%(msg),msg)
                mails=findall('<entry>(.*?)</entry>',r)
                count=1
                for mail in mails:
                    sender=parser('name',mail)
                    address=parser('email',mail)
                    subject=parser('title',mail)
                    summary=parser('summary',mail)
                    if len(subject)==0: subject="No Subject"
                    if len(summary)==0: summary="Email Body NOT present"
                    if count>new_emails:
                        break
                    try:
                        if new_emails==1:
                            display("FROM :  %s\nSUBJECT :  %s\n%s" %(sender.title()+' -> '+address.lower(),subject,summary),"%s writes about %s and says %s"%(sender,subject,summary))
                        else:
                            display("FROM :  %s\nSUBJECT :  %s\n%s" %(sender.title()+' -> '+address.lower(),subject,summary),"%s mail is from %s, %s %s. %s %s"%(speak(count),sender,random.choice([' and the Subject is ',' its about ']),subject,random.choice(['It says ',sender+' writes ']),summary))
                        count+=1
                    except: pass
                root.destroy()
                notify("Gmail!",'You have %d UNREAD email(s)' % unread)
            old_emails=unread
            sleep(60)
            if time()-timer>600:
                timer=time()
                if unread>0:
                    notify("Gmail!",'You have %d UNREAD email(s)' % unread)
        except: pass
