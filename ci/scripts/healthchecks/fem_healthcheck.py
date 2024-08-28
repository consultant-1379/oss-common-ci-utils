#!/usr/bin/env python3
#
# COPYRIGHT Ericsson 2023
#
#
#
# The copyright to the computer program(s) herein is the property of
#
# Ericsson Inc. The programs may be used and/or copied only with written
#
# permission from Ericsson Inc. or in accordance with the terms and
#
# conditions stipulated in the agreement/contract under which the
#
# program(s) have been supplied.
#

# Libraries
import requests
from requests import get
import os
import sys
import os.path
import subprocess
from os import path
from datetime import datetime

# Variables
# FEM
fem_instances = ["fem1s11","fem2s11","fem3s11", "fem4s11", "fem5s11", "fem6s11", "fem7s11", "fem8s11", "fem9s11"]
fem_instance_url = "https://instance-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/"
fem_login_command = "ssh -l ossadmin -p 53801 instance-eiffel216.eiffel.gic.ericsson.se version"

# Jenkins's environment variables
MAIL = os.environ['EMAIL']
JOB_URL = os.environ['JOB_URL']
BUILD_NUMBER = os.environ['BUILD_NUMBER']

# Report Generation
health_check_report = "healthcheck_file.txt"
email_file_name = "EmailToSend.txt"


# Common Functions
def exProces(command):
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdoutdata, stderrdata = proc.communicate()
    return (stdoutdata, stderrdata, proc)

# FEM Healthcheck
def femAccessCheck():
    for instance in fem_instances:
        instanceURL = fem_instance_url.replace("instance",instance)
        command = fem_login_command.replace("instance",instance)
        stdoutdata, stderrdata, proc = exProces(command)
        if stderrdata:
            with open(health_check_report, "a") as outputFile:
                outputFile.write("FEM: " + instanceURL + " - Connection_Unsuccessful\n")

        if stdoutdata:
            with open(health_check_report, "a") as outputFile:
                outputFile.write("FEM: " + instanceURL + " - Connection_Successful\n")

#Sending an Email Notification
def createEmail():
    healthCheckData= ""        # Holds all healthcheck records
    filteredHealthCheckData=[] # Holds only "Connection_Unsuccessful" healthcheck records
    job_name=JOB_URL.rsplit('/')[-2]

    # Create Email Content
    if path.exists(health_check_report):
        # Read Healthcheck Data from file
        with open(health_check_report) as inputFile:
            healthCheckData = inputFile.read().rstrip()
        inputFile.close()

        if healthCheckData:
            for data in healthCheckData.split("\n"):
                if "Connection_Unsuccessful" in data:
                    filteredHealthCheckData.append(data)

        if filteredHealthCheckData:
            emailHeader = (
                """<html> <head> <style> html, body { margin: 0 auto !important; padding: 0 !important; height: 100% !important; width: 100% !important; background:#fff;font-family: Arial,sans-serif;color: #333; } * {-ms-text-size-adjust: 100%;} </style> </head> <body width="100%" style="margin: 0; padding: 0 !important; mso-line-height-rule: exactly;"> <div style="text-align:center; background-color:rgb(155,150,10); color:#fff; "> <br><h2><i>"Functional User Access/login issue detected"</i></h2><br> </div><br><br><br>"""
            )
            with open(email_file_name, "a") as outputFile:
                outputFile.write(emailHeader)
                outputFile.write("""<p>The following instances failed at connectivity check:</p><br>""")
            outputFile.close()

            # Write Healthcheck data with "Connection_Unsuccessful"
            for data in filteredHealthCheckData:
                with open(email_file_name, "a") as outputFile:
                    outputFile.write(data + "<br><br>")
            with open(email_file_name, "a") as outputFile:
                outputFile.write("""<br><p>Please verify.</p>""")
                outputFile.write("""<br><p></p><p>Regards, <br>Team Hummingbirds</p> <p>Note: This mail was automatically sent after issues were detected in the jenkins job: <a href=""" + JOB_URL + BUILD_NUMBER + """>""" + job_name + """</a></p> </div> </body></html>""")
            outputFile.close()

            commandEmail = (
                """( echo To: """ + MAIL + """
                echo From: "jenkins-ossadmin-no-reply@ericsson.com"
                echo "Content-Type: text/html; "
                echo Subject: "Functional User Access/login issue detected"
                cat EmailToSend.txt ) | sendmail -t"""
            )
            stdoutdata, stderrdata, proc = exProces(commandEmail)
        else:
            print("-------------- Everything is working as expected-------------- ")
    else:
        print(health_check_report + "is not found!")


# Main Function
def main():

    if len(sys.argv) != 2:
        print("Function name not supplied")
        exit()

    functionName = sys.argv[1]
    if functionName == "FEM":
        femAccessCheck()
    elif functionName == "Email":
        createEmail()

if __name__ == "__main__":
    main()
