import requests
from lxml import etree
from popup import notify
from tkinter import Tk,Label
import time
import re
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'}

size=10
root=Tk()
root.title('Match Summary')
w,h,=250,150
root.geometry('%dx%d-%d-%d' % (w, h,0,40))
root.overrideredirect(True)
root.wm_attributes("-topmost", 1)
line1=Label(root,font=("Times", size+2))
line2=Label(root,font=("Times", size+2))
line3=Label(root,font=("Times", size))
line4=Label(root,font=("Times", size))
line5=Label(root,font=("Times", size))
line6=Label(root,font=("Times", size))
line7=Label(root,font=("Times", size))
for x in [line1,line2,line3,line4,line5,line6,line7]:
    x.pack()
line2.config(text='Please wait...')
root.update()

def show(data):
    dict={0:37,1:44,2:44}
    stack=list(data)
    stack+=['']*(7-len(stack))
    def display():
        for x,msg in zip([line1,line2,line3,line4,line5,line6,line7],stack):
            x.config(text=msg[:44])
        root.update()
    high=44
    for x in range(7):
        if len(stack[x])>dict[int((x+1)/3)]:stack[x]='       '+stack[x]+'    '
        if len(stack[x])>high: high=len(stack[x])
    if high>44:
        count=0
        while count<high:
            count+=1
            for x in range(7):
                if len(stack[x])>dict[int((x+1)/3)]:
                    stack[x]=stack[x][1:]+stack[x][0]
            display()
            time.sleep(.3)
    else:
        display()

def get_url():
    page=etree.HTML(requests.get("http://www.espncricinfo.com/ci/engine/match/index.html?view=live",headers=headers).text)
    section=1
    while True:
        x=page.xpath('//*[@id="live-match-data"]/section[%d]/section/div/text()'%section)
        section_matches=len(x)/16
        if section_matches==0: break
        elif section_matches>1:
            heading=page.xpath('//*[@id="live-match-data"]/div[%d]/h2/text()'%section)[0]
            matches=[]
            sub_section=1
            while True:
                y=page.xpath('//*[@id="live-match-data"]/section[%d]/section[%d]/div/text()'%(section,sub_section))
                if len(y)==0: break
                [t1,ignore,t2]=y[4:7]
                match=t1.strip(' ').strip('\n')+' Vs. '+t2.strip(' ').strip('\n')
                matches.append(match)
                sub_section+=1
            vector=min(6,len(matches))
            #show(["Live Matches are...",heading]+matches[0:vector])
            #time.sleep(vector*2)
        else:
            heading=page.xpath('//*[@id="live-match-data"]/div[%d]/h2/text()'%section)[0]
            [t1,ignore,t2]=x[4:7]
            match=t1.strip(' ').strip('\n')+' Vs. '+t2.strip(' ').strip('\n')
            #show(["Live Matches are...",heading,match])
            #time.sleep(3)
            if 'India' in match and 'Women' not in match and 'Rest' not in match: url,target="http://www.espncricinfo.com"+page.xpath('//*[@id="live-match-data"]/section[%d]/section/div[1]/span[3]/a'%section)[0].get('href'),match
        section+=1
    try:
        show(["Retriving info for",target])
        return url
    except:
        show(["","India is NOT playing",'','I may be wrong','So put URL in link.txt file','and put it in the same folder','EXITING...'])
        time.sleep(3)
        return ''
url=get_url()
count=0
while len(url)==0 and count<10:
    try:
        with open('link.txt') as f:
            for line in f:
                url=line
                break
    except: pass
    count+=1
    

situation=''
if len(url)>0:
    with requests.Session() as session:
        while 'won' not in situation or 'toss' in situation:
            first_team=second_team=situation=batsman_one=batsman_two=xrun_rate=run_rate=over_string=''
            loaded=False
            while loaded == False:
                try:
                    raw=session.get(url+'?version=iframe;view=live',headers=headers).text
                    page=etree.HTML(raw)
                    loaded=True
                except: pass
            try: [first_team,second_team,situation]=page.xpath('.//div[6]/div/div[1]/div[1]/p/text()')[0:3]
            except: pass
            if ' ov' in second_team: innings='Second'
            else: innings='First'
            try:
                 m = re.findall( '<tt>(.*?)</tt>', raw)[0]
                 for temp in ['<b>','</b>','<sup>','</sup>']: m=m.replace(temp,'')
                 m=m.replace('lb','(lb)').replace('wd','(wd)').replace('.','0').replace('nb','(nb)').split('|')
                 over_string=m[-1]
            except: pass
            try:
                name_one=page.xpath('.//table[1]/tr[4]/td[2]/a/text()')[0]
                b1R=int(page.xpath('.//table[1]/tr[4]/td[3]/b/text()')[0])
                b1B=int(page.xpath('.//table[1]/tr[4]/td[4]/text()')[0])
                if b1B>0:batsman_one='%s - %d (%d) || SR: %.2f' % (name_one,b1R,b1B,b1R*100/b1B)
                else:batsman_one='%s - %d (%d) || SR: 0.00' % (name_one,b1R,b1B)
                name_two=page.xpath('.//table[1]/tr[5]/td[2]/a/text()')[0]
                b2R=int(page.xpath('.//table[1]/tr[5]/td[3]/b/text()')[0])
                b2B=int(page.xpath('.//table[1]/tr[5]/td[4]/text()')[0])
                if b2B>0:batsman_two='%s - %d (%d) || SR: %.2f' % (name_two,b2R,b2B,b2R*100/b2B)
                else:batsman_two='%s - %d (%d) || SR: 0.00' % (name_two,b2R,b2B)
            except: pass
            try: over_string="Bowler: "+page.xpath('.//div[6]/div/div[2]/table[1]/tr[8]/td[2]/a/text()')[0].strip('*')+' - '+over_string
            except:over_string=''
            try:
                run_rate=page.xpath('.//div[2]/ul/li[1]/text()')[-1].replace('\n','').replace('\t','')
                if len(run_rate)==0: run_rate='--'
                xrun_rate=page.xpath('.//div[2]/ul/li[2]/b[1]/text()')[0]+': '+page.xpath('.//div[2]/ul/li[2]/text()[1]')[-1].strip(' ')+'-'+page.xpath('.//div[2]/ul/li[2]/text()[2]')[-1].strip(' ')
                RR='Run Rate: '+run_rate+' || '+xrun_rate
            except: RR='Run Rate: '+run_rate
            RR=RR.replace('\n','').replace('\t','')
            if innings is 'First':
                show([second_team+' VS.',   first_team,  batsman_one,  batsman_two,  over_string,  RR,   situation])
            else:
                try:calculations='    '+page.xpath('.//div[6]/div/div[1]/div[2]/ul/li[3]/b/text()')[0]+page.xpath('.//div[6]/div/div[1]/div[2]/ul/li[3]/text()')[0]
                except:calculations=''
                show([first_team+' VS.',  second_team,  batsman_one,  batsman_two,   over_string,  RR+calculations,  situation])
        else:
            notify(situation,first_team+'\n'+second_team,t=20)
root.destroy()
