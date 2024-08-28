#!/usr/bin/python

'''
this script is able to detect if LDAP configuration for each Jenkins instance
was modified thorugh the days. AN .html file will be created in order to help
the user during the detection phase: https://fem1s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/view/Monitoring/job/Admin_check_LdapPasswordIntegrity
'''

from datetime import date, timedelta
from xml.etree import ElementTree as et
from xml.dom import minidom
import lxml.etree as ET
import collections
import filecmp
import os
import time
import sys
import shutil
import subprocess
from datetime import datetime
import os.path
from os import path

tokenRef = {}
tokenList = []
ERROR = "False"

# import Jenkins's environment variables
JOB_URL = os.environ['JOB_URL']
BUILD_NUMBER = os.environ['BUILD_NUMBER']
MAIL = os.environ['MAIL']
wsPath = JOB_URL + BUILD_NUMBER + "/execution/node/3/ws/"

def exProces(command):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdoutdata, stderrdata = proc.communicate()
    return (stdoutdata, stderrdata, proc)


# List of Jenkins isntances to check
tree = ET.parse("/home/ossadmin/IDUN_repo/jenkins.xml")
roots = tree.getroot()
fems = []

for elem in roots.getiterator():
    fems.append(elem.tag) # indent this by tab, not two spaces as I did here
del fems[0] # remove maven2-moduleset tag
del fems[0]
today = time.strftime("-%Y-%m-%d")
yesterday = date.today() - timedelta(1)
yesterday = yesterday.strftime("-%Y-%m-%d")

tokenfileToday = open('test' + today + '.txt', 'w')
EmailToSend = open('CheckResults.html', 'w+') # text file containing e-mail to send

todaytokenList = []
yesterdaytokenList = []

# ################################################################# #
# DE Infrastructure Services and Tools Health Check E-mail creation #
# ################################################################# #
starterEmail = """<html>
<head>
<style>
table, th, td {
    border: 1px solid black;
    padding: 15px;
    text-align: center;
}
</style>
</head>
<body>"""
titleEmail = """<h2>eiffel216 ldap password Check</h2>"""
EmailToSend.write(starterEmail)
EmailToSend.write(titleEmail)

EmailToSend.write("""<table border = "1">""")
EmailToSend.write("""<tr><th bgcolor="#C6EFCE">FEM</th><th bgcolor="#C6EFCE">TOKEN</th></tr>""")
# ###################################################################

for fem in fems:
    fem = str(fem)
    jenkins_home = "/proj/eiffel216_config_" + fem + "/eiffel_home/"

    xml = minidom.parse(os.path.join(jenkins_home, "config.xml"))

    try:
        bindPassword = xml.getElementsByTagName("bindPassword")
        bindPassword = bindPassword[len(bindPassword) -1].firstChild.data
        token = bindPassword
        tokenList.append(token)
    except:
        token = "not available"
        pass

    tokenRef[fem] = token
    tokenfileToday.write(fem + "=" + token + "\n")

tokenRefod = collections.OrderedDict(sorted(tokenRef.items()))

yesterdayf = open('test' + yesterday + '.txt')
for line in yesterdayf:
    jenkinsRef = line.split('=')[0]
    yesterdaytokenList.append(line.replace(jenkinsRef + "=",""))

for index, (key, value) in enumerate(tokenRefod.iteritems()):

    count = 0
    for tokencode in tokenList:
        if tokencode == value:
            count += 1

    # remove whitespaces from strings to compare
    value = "".join(value.split())
    yesterdaytoken = "".join(yesterdaytokenList[index].split())

    if value == yesterdaytoken: # if token value is the same as yesterday
        if count > 1: # if token is used in multiple FEM
            EmailToSend.write("""<tr><th bgcolor="#FFFF00">""" + key + """</th><th bgcolor="#FFFF00">""" +  value + """</th></tr>""") # Yellow
        else:
            EmailToSend.write("""<tr><th>""" + key + """</th><th>""" +  value + """</th></tr>""")
    else: # if token value is not the same as yesterday
        if count > 1: # if token is used in multiple FEM
            EmailToSend.write("""<tr><th bgcolor="#FF1C00">""" + key + """</th><th bgcolor="#FF1C00">""" +  value + """</th></tr>""") # Vivid red
            ERROR = "True"
        else:
            EmailToSend.write("""<tr><th bgcolor="#FF6600">""" + key + """</th><th bgcolor="#FF6600">""" +  value + """</th></tr>""") # orange
            ERROR = "True"

EmailToSend.write("""</table>""")

EmailToSend.write("""<h1 style="background-color:#FFFF00;">Same token for multiple FEM</h1>""")
EmailToSend.write("""<h1 style="background-color:#FF6600;">Token has been changed through the days</h1>""")
EmailToSend.write("""<h1 style="background-color:#FF1C00;">Token has been changed through the days and it's available in multiple FEM</h1>""")

EmailToSend.write("""</body></html>""")

def createEmail():
    with open("emailToSend.html", "w") as emailText:
        with open("CheckResults_different.html", "r") as errorFile:
            for line in errorFile.readlines():
                emailText.write(line)


tokenfileToday.close()
EmailToSend.close()

if ERROR == "True":
    shutil.copyfile('CheckResults.html', 'CheckResults_different.html')
    print("-----------------------------------------------------------------------------------")
    print("ISSUES have been recorded into " + wsPath + "commandsError.txt")
    print("-------------- email is sent to " + MAIL + " -------------- ")
    createEmail()
    commandEmail = """( echo To: """ + MAIL + """
    echo From: "jenkins-ossadmin-no-reply@ericsson.com"
    echo "Content-Type: text/html; "
    echo Subject: "Functional User(FU) Ldap Integrity check failed"
    cat emailToSend.html ) | sendmail -t"""
    stdoutdata, stderrdata, proc = exProces(commandEmail)
    sys.exit(1)
