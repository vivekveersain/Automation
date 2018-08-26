# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 20:00:45 2017

@author: vvivek
"""

import paramiko, time, codecs, threading, os
from datetime import datetime, timedelta

class ssh():
    def __init__(self, host = '', username = "", hdipaqa = True):
        print("Connecting to: %s" % host)
        decryption = self._decrypt()
        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        try: self.client.connect(host, 22, username, decryption, look_for_keys = False)
        except:
            print("Authentication failed.")
            self._encrypt()
            decryption = self._decrypt()
            self.client.connect(host, 22, username, decryption, look_for_keys = False)
        self.transport = paramiko.Transport((host, 22))
        self.transport.connect(None, username, decryption)
        self.openShell()
        time.sleep(1)
        self._reader()
        self.hdipaqa = hdipaqa
        if hdipaqa: self.cmd("sudo -i -u hdipaqa")
    
    def _reader(self):
        if self.shell != None and self.shell.recv_ready():
            alldata = self.shell.recv(1024)
            while self.shell.recv_ready():
                alldata += self.shell.recv(1024)
            strdata = str(alldata, "utf8").replace('\r', '').strip("\n")
            print(strdata)
            return strdata[-2:]
        else: 
            time.sleep(1)
            return ''
    
    def _decrypt(self):
        with open(r"C:\Users\vvivek\Documents\keys.txt") as f: data = f.read()
        return codecs.decode(bytes(data, encoding="utf-8"), 'base64').decode("utf-8")
    
    def _encrypt(self):
        data = input("Enter: ")
        if not data: return
        with open(r"C:\Users\vvivek\Documents\keys.txt", 'wb') as f:
            f.write(codecs.encode(bytes(data, encoding = "utf-8"), encoding="base64"))

    def closeConnection(self):
        if(self.client != None):
            self.client.close()
            self.transport.close()
 
    def openShell(self):
        self.shell = self.client.invoke_shell()
 
    def cmd(self, command):
        if(self.shell):
            self.shell.send(command + "\n")
            while True:
                if self._reader() == "$ ": return
        else:
            print("Shell not opened.")
    
    def week_dates(self, weeknr = 1):
        if weeknr<100: weeknr += 201800
        weeknr = weeknr%100
        yr_start = datetime.strptime('04-02-2018',"%d-%m-%Y")
        week_start = yr_start + timedelta(weeks = weeknr - 1)
        week_end = week_start + timedelta(days = 6)
        return week_start.strftime('%Y-%m-%d') +"|"+ week_end.strftime('%Y-%m-%d')
    
    def _download_mngr(self):
        while self._downloading:
            try: dwnlded = os.stat(self.trget).st_size
            except: dwnlded = 0
            print("\rDownloading at %.2f%%  " %(dwnlded*100/self.totl_size), end = '')
        try: self._thread._stop()
        except: pass
    
    def download_file(self, src, dest):
        try:
            sftp = self.client.open_sftp()
            self._downloading = True
            self.totl_size = int(self.client.exec_command("stat -c %s " + src)[1].read().decode().strip('\n'))
            self.trget=dest
            self._thread = threading.Thread(target=self._download_mngr)
            self._thread.daemon = True
            self._thread.start()
            sftp.get(src, dest)
            sftp.close()
        except FileNotFoundError: print("\n\nFILE NOT Found\n\n")
        except Exception as e: print(e, e.__doc__)
        self._downloading = False
    
    def unix_to_hadoop(self, src, dest, del_src = False):
        print("Moving from Unix(%s) to Hadoop(%s)" % (src, dest))
        if not self.hdipaqa:
            print("Not enough permissions! Log In as HDIPAQA")
            return False
        self.cmd("hadoop fs -put %s %s" % (src, dest))
        if del_src: self.cmd("hadoop fs -rm %s" % src)
        return True
    
    def hadoop_to_unix(self, src, dest = None, merge = True, del_src = False):
        print("Moving from Hadoop(%s) to Unix(%s)" % (src, dest))
        if not dest:
            if self.hdipaqa: dest = 'dest'
            else: dest = 'dest'
        if merge: action = "-getmerge"
        else: action = "-get"
        self.cmd("hadoop fs %s %s %s" % (action, src, dest))
        if del_src: self.cmd("hadoop fs -rm %s" % src)
        return True
    
    def send_mail(self, to, subject, message):
        if type(to) == list: to = " ".join(to)
        self.cmd("echo %s>message.txt"%message)
        self.cmd('mutt -s "%s" %s<message.txt'%(subject, to))

class AdHoc():
    def __init__(self, fmt, connection = None):
        if not connection: self.connection = ssh()
        else: self.connection = connection()
        self.fmt = fmt
        if fmt == "S" : self.connection.cmd("cmd")
        else: self.connection.cmd("cmd")
        self.week = 0
    
    def run_for(self, weeknr, public = False, local = True):
        if type(weeknr) is int: 
            self.week = weeknr
            self.dates = self.connection.week_dates(self.week)
        else:
            self.dates = weeknr
        self.run_shell()
        if public: self.move_file()
        if local: self.move_file(local)
    
    def run_shell(self, dates = None):
        print("Running Ad-hoc for: %s -> %d [%s]" %(self.fmt, self.week, self.dates))
        self.connection.cmd("echo '%s\n' >start_end_date.txt" % self.dates)
        if self.fmt =="S" : self.connection.cmd("command")
        else : self.connection.cmd("command")
    
    def move_file(self, local = True):
        print("MOVING FILES -------->\n")
        name = self.fmt+ "_" + str(self.week)+".txt"
        if local: dest = name
        else: dest = r"dest" + "\%s"%(name)
        if self.fmt == "S": self.connection.download_file("fine_name", dest)
        else : self.connection.download_file("file_name", dest)
        if local:
            with open(name) as f: data = f.read().replace(",","^").replace("|",",")
            with open(self.fmt + '_' + str(self.week)+".csv", "w") as f: f.write(data)
        self.connection.closeConnection()
'''
for fmt in ("K", "S"): 
    for x in range(201805, 201808):
        adhoc = AdHoc(fmt)
        adhoc.run_for(x, False, True)
'''

input("\n\nComplete...")