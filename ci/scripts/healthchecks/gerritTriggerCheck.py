#!/usr/bin/python

'''
By using this script it will be possible to check the result of https://femXXX-eiffel216.lmera.ericsson.se:8443/jenkins/job/Admin_Gerrit_Trigger_Test/.
If the Gerrit Trigger doesn't work for a specific Jenkins instance the following string will be shown -> Jenkins Job was not triggered
'''

import os
import os.path
import subprocess
import datetime
import sys
import urllib2
import xml
import requests
from os import path
from xml.dom import minidom
from datetime import datetime
from requests.auth import HTTPBasicAuth
from os import path
reload(sys)
sys.setdefaultencoding('utf-8')

OSSADMIN_USER = os.environ.get('OSSADMIN_USER')
OSSADMIN_PASS = os.environ.get('OSSADMIN_PASS')

jenkins_instances = ["1s11", "2s11", "3s11", "4s11", "5s11", "6s11", "7s11", "8s11"]
timeDelta = 9000

todayTime = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
todayTime = datetime.strptime(todayTime, "%Y-%m-%d %H:%M:%S")

# ############################################ #
# Parsing .xml file by tag value               #
# ############################################ #
def getValueFromTag(ConfigFile, tag):
    try:
        xmldoc = minidom.parse(ConfigFile)
        return xmldoc.getElementsByTagName(tag)
    except urllib2.HTTPError as err:
        if err.code == 404:
            pass
    except xml.parsers.expat.ExpatError, e:
        pass

# ############################################ #
# Parsing .xml file by tag value               #
# ############################################ #
def getRestApiXML(jenkins_instance, rest_command, file_name):
    RestAPI = open(file_name, 'w')
    try:
        # http request in order to fill .xml file with information
        r = requests.get(rest_command, verify=False, auth=HTTPBasicAuth(OSSADMIN_USER, OSSADMIN_PASS))
        print(r)
        RestAPI.write(r.text)
        return True
    except IndexError, e:
        print(str(e) + "\nMissing API Token for " + jenkins_instance)
        return False
    except UnicodeEncodeError, e:
        print(str(e) + "\nNot possible to retrieve information from " + rest_command)
        return False
    RestAPI.close()

for jenkins_instance in jenkins_instances:
    # get .xml file from REST API for jobs queue details
    fem_name="fem"+jenkins_instance
    rest_command = "https://" + fem_name + "-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/Admin_Gerrit_Trigger_Test_PreCodeReview/lastBuild/api/xml"
    print(rest_command)
    getRestApiXML(fem_name, rest_command, "lastBuildAPI.xml")

    buildDate = getValueFromTag("lastBuildAPI.xml", "date")
    buildResult = getValueFromTag("lastBuildAPI.xml", "result")

    try:
        try:
            buildTime = datetime.strptime(buildDate[0].firstChild.nodeValue, "%Y-%m-%d %H:%M:%S +%f")
            buildTime = buildTime.strftime("%Y-%m-%d %H:%M:%S")
            buildTime = datetime.strptime(buildTime, "%Y-%m-%d %H:%M:%S")
            print(buildTime)
        except:
            buildTime = datetime.strptime(buildDate[0].firstChild.nodeValue, "%Y-%m-%dT%H:%M:%S+%f")
            buildTime = buildTime.strftime("%Y-%m-%dT%H:%M:%S")
            buildTime = datetime.strptime(buildTime, "%Y-%m-%dT%H:%M:%S")
            print(buildTime)

        delta_in_seconds = (todayTime - buildTime).total_seconds()
        print(delta_in_seconds)
        if delta_in_seconds < timeDelta:
            if buildResult[0].firstChild.nodeValue == 'SUCCESS':
                print "fem" + jenkins_instance + ": " + buildResult[0].firstChild.nodeValue
            else:
                print "fem" + jenkins_instance + ":  " + buildResult[0].firstChild.nodeValue + "  ==> https://fem" + jenkins_instance + "-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/Admin_Gerrit_Trigger_Test_PreCodeReview"
        else:
            print "fem" + jenkins_instance + ": Jenkins Job was not triggered " + "https://fem" + jenkins_instance + "-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/Admin_Gerrit_Trigger_Test_PreCodeReview"
            sys.exit(1)
    except IndexError as error: #manage HANGING process or issue with concurrent gerrit reviews -> https://stackoverflow.com/questions/34271912/random-error-from-gerrit-cli-over-ssh-cannot-post-review
        print "fem" + jenkins_instance + ": " + "https://fem" + jenkins_instance + "-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/Admin_Gerrit_Trigger_Test_PreCodeReview"
        continue