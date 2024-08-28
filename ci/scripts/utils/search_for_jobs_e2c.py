#!/usr/bin/python
'''
Search for strings in Jenkins Job's configuration (config.xml).
Example of usage:
- stringToSearch = "test.coverage"
- jenkins_instance = "fem1s11"
- job_type = "Release"
'''
from xml.etree import ElementTree as ET
import subprocess
from xml.dom import minidom
import urllib2
import xml
import sys
import os
fems = []
# Script's arguments
stringToSearch  = sys.argv[1] # the string to search inside Jenkins Job's config.xml files
jenkins_instance  = sys.argv[2] # the Jenkins Instance where to check for config.xml files
job_type  = sys.argv[3] # filter by Job's type (e.g. PreCodeReview, Publish, ...)
print '''====================================================================================
Searching ''' + stringToSearch + ''' type: ''' + job_type + ''' in jenkins: ''' + jenkins_instance + '''
====================================================================================
'''
if jenkins_instance == "all":
    fems = ["fem1s11","fem2s11","fem3s11","fem4s11","fem5s11","fem6s11","fem7s11","fem8s11"]
else:
    fems = [jenkins_instance]
for fem in fems:
    listOfJobs = open('listOfJobs.txt', 'w')
    stringFound = 0
    jenkins_url = "https://" + fem + "-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/"
    jenkins_path = "/proj/eiffel216_config_" + fem + "/eiffel_home/"
    # list all Jenkins Jobs
    listAllJobs = "ssh -l ossadmin -p 53801 " + fem + "-eiffel216.eiffel.gic.ericsson.se list-jobs All | grep -v 'Skipping' > listAllJobs.txt"
    proc = subprocess.Popen(listAllJobs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = proc.stdout.read()
    if os.stat("listAllJobs.txt").st_size != 0:
        with open("listAllJobs.txt") as textFile:
            for jenkins_job in textFile:
                jenkins_job = " ".join(jenkins_job.split()) # remove whitespaces from string
                configFile = jenkins_path + "jobs/" + jenkins_job + "/config.xml"
                try:
                    tree = ET.parse(configFile)
                    roots = tree.getroot()
                except xml.etree.ElementTree.ParseError:
                    print("Not able to parse config file",configFile)
                except IOError,e:
                    continue # in case of not existing config.xml file
                if stringToSearch in open(configFile).read():
                    stringFound += 1
                    if job_type == "all":
                        listOfJobs.write(jenkins_url + "job/" + jenkins_job + "\n")
                    else:
                        if job_type in jenkins_job:
                            listOfJobs.write(jenkins_url + "job/" + jenkins_job + "\n")
            listOfJobs.close()
            if stringFound != 0:
                print("\n")
                print(fem)
                with open('listOfJobs.txt', 'r') as listOfJobs:
                    print(listOfJobs.read())
    else:
        print(fem + " is not reachable or it doesn't have any Jenkins Jobs!\n")