import sys
import glob
import os
import urllib2
import requests
from requests.auth import HTTPDigestAuth
import json
import socket
import smtplib

def GetServerData(localip):
 websitelist = []
 wb = []
 url = "http://devtracker.devdigital.com/index.php?route=api/dev/getServerDetail&server_ip2={}". format(localip)
 header={'Content-Type':'application/json', 'Accept':'application/json', 'Authorization':'Basic ZGV2dHJhY2tlcjpkZXZ0cmFja2VyQDA4MTY='}
 user = 'devtracker'
 passwd = 'devtracker@0816'
 resp = requests.get(url,auth=HTTPDigestAuth(user,passwd),headers=header, verify=True)
 if(resp.ok):
  jData = json.loads(resp.content)
  for key in jData:
   if(format(key)=='values'):
	for arr in jData['values']:
	 websitelist.extend(arr['all_url'])
 wb = [str(i) for i in websitelist]
 return wb
def filter_content(content,strs):
	emptylist = []
	pos = content.index(strs)
	if(pos == 0):
		rlst = content.replace(strs, "").strip().rsplit(" ") if (content.replace(strs, "").strip().count(" ") > 0) else [content.replace(strs, "").strip()]
		return rlst
	else:
		return emptylist
def send_email(sname,wlist,dlist):
	#datagrid = urllib2.urlopen("http://192.168.10.30/data_grid.html").read()
	datagrid = urllib2.urlopen("http://192.168.10.30/template_demo.html").read()
	#template = urllib2.urlopen("http://192.168.10.30/template.html").read()
	
	websites = "<br>".join(wlist)
	websites2 = "<br>".join(dlist)
	data = datagrid.replace('SERVER_NAME', sname).replace('DT_WEBSITE_LIST',websites).replace('SRV_WEBSITE_LIST',websites2)
	#msg = template.replace('DATA_GRID', data)
	msg = data
	message = """From: info@devdigital.com
To: servers@devdigital.com
MIME-Version: 1.0
Content-type: text/html
Subject: """+ sname + """ Server Website status

"""
	server = smtplib.SMTP('cpanel.wvmagicdesign.com', 587)
	server.login("info@devdigital.com", "Utopia37211")
	server.sendmail("info@devdigital.com", "servers@devdigital.com", message+msg)

def DiffList(li1, li2): 
 #dif = [i for i in li1 + li2 if i not in li1 or i not in li2] # or i.startswith('www.') 
 comm = []
 li_dif = []
 for i in li1:
  if i.startswith('*'):
   #print(i)
   w = i.replace('*.', "",1)
  elif i.startswith('www.'):
   w = i.replace('www.', "",1)
  else: w = i
  w2 = "www." + w
  w3 = "*." + w
  
  if (w in li2 or w2 in li2 or w3 in li2) or w == "aaaawvmagic.com" :
   comm.append(i)
  else:
   #if "*.aaaawvmagic.com" != i or "aaaawvmagic.com" != i:
   li_dif.append(i)
 return li_dif 
def CommonList(li1, li2): 
 li_dif = [i for i in li1 + li2 if i in li1 and i in li2] 
 return li_dif
def main():
	weblist = []
	hostname = socket.gethostname()
	os.chdir( "/etc/httpd/conf.d/" )
	if len(sys.argv) > 1:
		localip = sys.argv[1]
	for file in glob.glob('*.conf'):
		with open(file) as fp:
			cnt = 0
			for line in fp:
				strline = line.strip()
				if 'ServerName' in strline:
					nlst = filter_content(strline,'ServerName')
					if (len(nlst) > 0): weblist.extend(nlst)
				if 'ServerAlias' in strline:
					nlst = filter_content(strline,'ServerAlias')
					if (len(nlst) > 0): weblist.extend(nlst)
	weblist = list(dict.fromkeys(weblist))
	weblst = GetServerData(localip)
	diffDT = DiffList(weblst, weblist)
	diffSRV = DiffList(weblist,weblst)
	#diffweb = diffDT + diffSRV
	send_email(hostname,diffSRV,diffDT)
if __name__ == '__main__':main()