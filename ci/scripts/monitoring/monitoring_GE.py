#!/usr/bin/python3

import re
import os
import sys
import time
import os.path
import subprocess
from os import path
from os.path import exists
from datetime import datetime


# Variables
passwordCheck = True                                                                           # Password Check Flag
fileSystemthreshold = 70                                                                       # GE and FEM disk space usage threshold
fileSystemCommand = " df -h "                                                                  # Disk space usage command
dockerFolder = "/local1"                                                                       # Target mount path for storing docker images
errorFileName = "Error_logs.txt"                                                               # Error log file
emailFileName = "EmailToSend.txt"                                                              # Email Text
femInstances = ["fem1s11","fem2s11","fem3s11", "fem4s11", "fem5s11", "fem6s11","fem7s11","fem8s11","fem9s11"]      # Jenkins instances for filesystem and connectivity check
femInstancesWorkspaceCleanup = ["fem1s11","fem3s11","fem6s11","fem9s11"]                                 # Jenkins instances for cleaning GE workspace
femLoginCommand = "ssh -l ossadmin -p 53801 instance-eiffel216.eiffel.gic.ericsson.se version" # FEM Login Command
femFolderList = ["/home/ossadmin", "/proj/mvn", "/proj/eiffel216_config_instance"]             # FEM filesystem folders
gridEngines = ["26249","25612","25159","24896","26247","25746","00297","06842","22354","22394","22395","22399","22400","24758","22342","26934","27025","19206","19511"]                # GE instances maintained by the Hummingbirds.
geLoginCommand = "qrsh -q ossmsci.q -l hostname=seliiusGE.seli.gic.ericsson.se"                # GE login command
twicCertificate = "eval $(twic profile env TSA_jenkins_profile_SUFIX)"                         # Twic certificate
senderEmail = "jenkins-ossadmin-no-reply@ericsson.com"                                         # Default sender email


# Report Files
consolidatedReport = "GE_Monitoring_Report.html"
femConnectionReport = "FEM_Connection_Report.csv"
femFileSystemReport = "FEM_FileSystem_Report.csv"
femFileSystemReportPreCleanup = "FEM_FileSystem_Report_PreCleanup.csv"
geConnectionReport = "GE_Connection_Report.csv"
geFileSystemReport = "GE_FileSystem_Report.csv"
geFileSystemReportPreCleanup = "GE_FileSystem_Report_PreCleanup.csv"
geQueueMonitoringReport = "GE_Queue_Monitoring_Report.csv"
geDockerSystemAnalysisReport = "InstanceName/InstanceName_Docker_System_Analysis_Report.csv"
geDockerContainerAnalysisReport = "InstanceName/InstanceName_Docker_Container_Analysis_Report.csv"
geDockerContainerCleanupReport = "InstanceName/InstanceName_Docker_Container_Cleanup_Report.txt"
geDockerImageAnalysisReport = "InstanceName/InstanceName_Docker_Image_Analysis_Report.csv"
geDockerImageCleanupReport = "InstanceName/InstanceName_Docker_Image_Cleanup_Report.txt"
geDockerVolumeCleanupReport = "InstanceName/InstanceName_Docker_Volume_Cleanup_Report.txt"
geDockerNetworkCleanupReport = "InstanceName/InstanceName_Docker_Network_Cleanup_Report.txt"
geDockerBuildCacheCleanupReport = "InstanceName/InstanceName_Docker_Build_Cache_Cleanup_Report.txt"


# Jenkins's environment variables
MAIL = os.environ['EMAIL']
JOB_URL = os.environ['JOB_URL']
BUILD_NUMBER = os.environ['BUILD_NUMBER']
wsPath = JOB_URL + BUILD_NUMBER + "/execution/node/3/ws/"




# Common Functions
def exProces(command):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdoutdata, stderrdata = proc.communicate()
    return (stdoutdata, stderrdata, proc)


# Returns GE Twic command
def getTwicCommand(instance):
    suffix = instance[-3:]
    if suffix == "896":
        command = twicCertificate.replace("_SUFIX", "")
    else:
        command = twicCertificate.replace("SUFIX", suffix)
    return command


# Returns GE Login command
def getLoginCommand(instance):
    return geLoginCommand.replace("GE", instance)


# Writes the Error Messages to a text file
def saveErrorLogs(errorMessage):
    with open(errorFileName, "a") as errorFile:
        errorFile.write(errorMessage)


# Creates a HTML Paragraph from the text file and writes it to the HTML report
def createHTMLTable(fileName):
    htmlString = "<table>"
    tableHeader = "<th>header</th>"
    tableData = "<td>data</td>"
    with open(fileName) as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
        count =1
        for line in lines:
                if count == 1:
                    htmlString = htmlString + '<tr style = "background-color: #b5b5b5;">'
                    for word in line.split(","):
                        temp = tableHeader.replace("header", word)
                        htmlString = htmlString + temp
                    htmlString = htmlString + "</tr>"
                else:
                    htmlString = htmlString + "<tr>"
                    for word in line.split(","):
                        temp = tableData.replace("data", word)
                        htmlString = htmlString + temp
                    htmlString = htmlString + "</tr>"
                count = count + 1
        htmlString = htmlString + "</table><br><br>"

        # Conditional Formatting
        htmlString = htmlString.replace(">Success", ' style="color:green">Success')
        htmlString = htmlString.replace(">Failed", ' style="color: red;">Failed')
        htmlString = htmlString.replace(">Running", ' style="color:green">Running')
        htmlString = htmlString.replace(">Exited", ' style="color:red">Exited')
        htmlString = htmlString.replace(">In-Use", ' style="color:green">In-Use')
        htmlString = htmlString.replace(">Unused", ' style="color:red">Unused')
        htmlString = htmlString.replace(">Dangling", ' style="color:red">Dangling')

    with open(consolidatedReport, "a") as reportFile:
        reportFile.write(htmlString)


# Adds a horizontal line to the HTML report
def addHorizontalLine():
    htmlString = "<hr>"
    with open(consolidatedReport, "a") as reportFile:
        reportFile.write(htmlString)


# Creates a HTML Paragraph from the text file and writes it to the HTML report
def createHTMLString(fileName):
    htmlString = "<p>"
    searchText = "Total reclaimed space"
    with open(fileName) as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
        for line in lines:
            # Conditional Formatting
            if searchText in line:
                line = "<p style='color:green'>" + line + "</p>"
            htmlString = htmlString + line + "<br>"
        htmlString = htmlString + "<p>"

    with open(consolidatedReport, "a") as reportFile:
        reportFile.write(htmlString)




# Prepare Jenkins Workspace
def prepareWorkspace():
    for instance in gridEngines:
        instanceName = "seliius" + instance
        command = "rm -rf instanceName && mkdir instanceName"
        command = command.replace("instanceName",instanceName) # command: rm -rf seliius26249 && mkdir seliius26249
        stdoutdata, stderrdata, proc = exProces(command)
        if proc.returncode == 0:
            print(instanceName + "/ directory has been created in the Jenkins workspace - " + wsPath + instanceName)

        if stderrdata:
            errorMessage = "Clean: " + instanceName + " - " + stderrdata.decode('utf-8').strip() + "\n"
            print(errorMessage)
            saveErrorLogs(errorMessage)




# FEM Monitoring Tasks
# FEM Connection
def femConnection():
    print("\n--------------- FEM Connection Check --------------------")
    reportFileName = femConnectionReport # FEM_Connection_Report.csv
    reportHeader = "FEM Instance,Connection Status,Comments\n"
    with open(reportFileName, "a") as reportFile:
        reportFile.write(reportHeader)

    for instance in femInstances:
        status = checkFEMConnection(instance, reportFileName)
        with open(reportFileName, "a") as reportFile:
            reportFile.write("\n")
    print("\nResults are saved to " + wsPath + reportFileName)
    print("--------------------------------------------------------")


def checkFEMConnection(instance, reportFileName):
    status=True
    command = femLoginCommand.replace("instance",instance) # Sample Command: ssh -l ossadmin -p 53801 fem1s11-eiffel216.eiffel.gic.ericsson.se version
    status = executeCheckFEMConnection(instance, command, reportFileName)
    return status


def executeCheckFEMConnection(instance, command, reportFileName):
    status=True
    instanceName = instance + "-eiffel216.eiffel.gic.ericsson.se"
    stdoutdata, stderrdata, proc = exProces(command)

    if stdoutdata:
        print(instanceName + " : Success")
        with open(reportFileName, "a") as reportFile:
            reportFile.write(instanceName + ",Success, -")

    if stderrdata:
        print(instanceName + " : Failed - " + stderrdata.decode('utf-8').strip())
        with open(reportFileName, "a") as reportFile:
            reportFile.write(instanceName + ",Failed," + stderrdata.decode('utf-8').strip().replace(",", " -"))

        # errorMessage = "FEM Connection: " + instanceName + " - " + stderrdata.decode('utf-8').strip() + "\n"
        # saveErrorLogs(errorMessage)
        status=False
    return status




# FEM FileSystem
def femFileSystem():
    print("\n------------------------------- FEM FileSystem Assessment ----------------------------------")
    executeFemFileSystemAnalysis('Pre-cleanup')
    print("\nResults are saved to " + wsPath + femFileSystemReportPreCleanup) # FEM_FileSystem_Report_PreCleanup.csv

    executeFemFileSystemCleanup()
    executeFemFileSystemAnalysis('Post-cleanup')
    print("\nResults are saved to " + wsPath + femFileSystemReport) # FEM_FileSystem_Report.csv
    print("--------------------------------------------------------------------------------------------")


# Check FEM filesystem memory usage
def executeFemFileSystemAnalysis(scanType):
    reportFileName = femFileSystemReport
    print(scanType + ":")
    if(scanType == "Pre-cleanup"):
        reportFileName = femFileSystemReportPreCleanup

    reportHeader = "File System,Total Space,Used Space,Available Space,Used Percentage,Threshold Status,Comments,Scan Type"
    with open(reportFileName, "a") as reportFile:
        reportFile.write(reportHeader)

    for folder in femFolderList:

        if "instance" not in folder:
            with open(reportFileName, "a") as reportFile:
                reportFile.write("\n" + folder + ",") # Adding default mount path to the report.
            command = fileSystemCommand + folder  # Sample Command: df -h /home/ossadmin , df -h /proj/mvn
            stdoutdata, stderrdata, proc = exProces(command)

            if stdoutdata:
                print(stdoutdata.strip())
                lines=stdoutdata.split("\n")
                elements = lines[1].split(" ")
                for elem in elements:
                    if elem != "" and "/" not in elem:
                        with open(reportFileName, "a") as reportFile:
                            reportFile.write(elem + ",")
                        if "%" in elem:
                            usedSpace = elem.replace("%", "")
                            if int(usedSpace) >= fileSystemthreshold: # Threshold validation
                                with open(reportFileName, "a") as reportFile:
                                    reportFile.write("Failed,Threshold of " + str(fileSystemthreshold) + "% exceeded.," + scanType)
                                if(scanType == "Post-cleanup"):
                                    errorMessage = "FEM FileSystem: " + folder + " physical memory usage exceeds the threshold (" + str(fileSystemthreshold)+ "%)\n"
                                    saveErrorLogs(errorMessage)
                            else:
                                with open(reportFileName, "a") as reportFile:
                                    reportFile.write("Success,-," + scanType)

            if stderrdata:
                errorMessage = "FEM FileSystem: " + folder + " - " + stderrdata.decode('utf-8').strip() + "\n"
                print(errorMessage)
                saveErrorLogs(errorMessage)
                with open(reportFileName, "a") as reportFile:
                    reportFile.write("-,-,-,-,Failed," + stderrdata.decode('utf-8').strip().replace(",", "-") + "," + scanType)

        else:
            for instance in femInstances:
                folderName = folder.replace("instance",instance)
                with open(reportFileName, "a") as reportFile:
                    reportFile.write("\n" + folderName + ",") # Adding default mount path to the report.
                command = fileSystemCommand + folderName  # Sample Command: df -h /proj/eiffel216_config_fem1s11
                stdoutdata, stderrdata, proc = exProces(command)

                if stdoutdata:
                    print(stdoutdata.strip())
                    lines=stdoutdata.split("\n")
                    elements = lines[1].split(" ")
                    for elem in elements:
                        if elem != "" and "/" not in elem:
                            with open(reportFileName, "a") as reportFile:
                                reportFile.write(elem + ",")
                            if "%" in elem:
                                usedSpace = elem.replace("%", "")
                                if int(usedSpace) >= fileSystemthreshold: # Threshold validation
                                    with open(reportFileName, "a") as reportFile:
                                        reportFile.write("Failed,Threshold of " + str(fileSystemthreshold) + "% exceeded.," + scanType)
                                    if(scanType == "Post-cleanup"):
                                        errorMessage = "FEM FileSystem: " + folderName + " physical memory usage exceeds the threshold (" + str(fileSystemthreshold)+ "%)\n"
                                        saveErrorLogs(errorMessage)
                                else:
                                    with open(reportFileName, "a") as reportFile:
                                        reportFile.write("Success,-," + scanType)

                if stderrdata:
                    errorMessage = "FEM FileSystem: " + folder + " - " + stderrdata.decode('utf-8').strip() + "\n"
                    print(errorMessage)
                    saveErrorLogs(errorMessage)
                    with open(reportFileName, "a") as reportFile:
                        reportFile.write("-,-,-,-,Failed," + stderrdata.decode('utf-8').strip().replace(",", "-") + "," + scanType)


# Cleanup /home/ossadmin directories
def executeFemFileSystemCleanup():

    # Cleanup /home/ossadmin/.m2/repository
    command = "cd /home/ossadmin/.m2/ && rm -rf repository"
    stdoutdata, stderrdata, proc = exProces(command)
    if stdoutdata:
        print(stdoutdata.strip())

    if stderrdata:
        errorMessage = "FEM FileSystem Cleanup: " + command + " - " + stderrdata + "\n"
        print(errorMessage)
        saveErrorLogs(errorMessage)

    # Cleanup home/ossadmin/mvn/.m2/repository
    command = "cd /home/ossadmin/mvn/.m2/repository && rm -rf *"
    stdoutdata, stderrdata, proc = exProces(command)
    if stdoutdata:
        print(stdoutdata.strip())

    if stderrdata:
        errorMessage = "FEM FileSystem Cleanup: " + command + " - " + stderrdata + "\n"
        print(errorMessage)
        saveErrorLogs(errorMessage)

# FEM Password
def mypasswdExist():
    print("\n----------------------------- Password Check ------------------------")
    command = "cat /home/ossadmin/mypasswd"
    stdoutdata, stderrdata, proc = exProces(command)

    if stdoutdata:
        passwordCheck = True # Global Variable
        print(stdoutdata.decode('utf-8').replace("\n", ""))
        print("Password Check: Success!")

    if stderrdata:
        passwordCheck = False # Global Variable
        errorMessage = "FEM Password: " + stderrdata.decode('utf-8').strip() + "\n"
        print(errorMessage)
        saveErrorLogs(errorMessage)
        print("Password Check: Failed!")
    print("---------------------------------------------------------------------")




# GE Monitoring Tasks
# GE Connection
def connection():
    print("\n--------------- GE Connection Check --------------------")
    reportFileName = geConnectionReport # GE_Connection_Report.csv
    reportHeader = "GE Instance,Connection Status,Comments\n"
    with open(reportFileName, "a") as reportFile:
        reportFile.write(reportHeader)

    for instance in gridEngines:
        status = checkConnection(instance, reportFileName)
        with open(reportFileName, "a") as reportFile:
            reportFile.write("\n")
    print("\nResults are saved to " + wsPath + reportFileName)
    print("--------------------------------------------------------")


def checkConnection(instance, reportFileName):
    status=True
    command = getLoginCommand(instance) + fileSystemCommand + dockerFolder  # Command: qrsh -q ossmsci.q -l hostname=seliius26249.seli.gic.ericsson.se df -h /local1
    status = executeCheckConnection(instance, command, reportFileName)
    return status


def executeCheckConnection(instance, command, reportFileName):
    status=True
    instanceName = "seliius" + instance
    stdoutdata, stderrdata, proc = exProces(command)

    if stdoutdata:
        print(instanceName + " : Success")
        with open(reportFileName, "a") as reportFile:
            reportFile.write(instanceName + ",Success, -")

    if stderrdata:
        print(instanceName + " : Failed - " + stderrdata.decode('utf-8').strip())
        with open(reportFileName, "a") as reportFile:
            reportFile.write(instanceName + ",Failed," + stderrdata.decode('utf-8').strip().replace(",", " -"))

        # Commenting the below lines to avoid unnecessary noise
        # errorMessage = "GE Connection: " + instanceName + " - " + stderrdata.decode('utf-8').strip() + "\n"
        # saveErrorLogs(errorMessage)
        status=False
    return status




# GE FileSystem Check
def fileSystem(scanType):
    print("\n--------------- GE FileSystem Assessment ---------------")
    reportFileName = geFileSystemReport # GE_FileSystem_Report.csv
    if scanType == "Pre-cleanup":
        reportFileName = geFileSystemReportPreCleanup # GE_FileSystem_Report_PreCleanup.csv

    reportHeaders = "GE Instance,Total Size,Used Space,Available Space,Used Percentage,Threshold Status,Comments,Scan Type\n"
    with open(reportFileName, "a") as reportFile:
        reportFile.write(reportHeaders)

    for instance in gridEngines:
        status = checkDiskSpace(instance, reportFileName, scanType)
        with open(reportFileName, "a") as reportFile:
            reportFile.write("\n")
    print("\nResults are saved to " + wsPath + reportFileName)
    print("--------------------------------------------------------")


def checkDiskSpace(instance, reportFileName, scanType):
    status=True
    command = getLoginCommand(instance) + fileSystemCommand + dockerFolder
    status = executeCheckSpace(instance, command, reportFileName, scanType)
    return status


def executeCheckSpace(instance, command, reportFileName, scanType):
    status=True
    instanceName = "seliius" + instance
    print(instanceName + " :")
    with open(reportFileName, "a") as reportFile:
        reportFile.write(instanceName + ",")

    stdoutdata, stderrdata, proc = exProces(command)

    if stdoutdata:
        print(stdoutdata.strip() + "\n")
        lines=stdoutdata.split("\n")
        elements = lines[1].split(" ")
        for elem in elements:
            if elem != "" and "/" not in elem:
                with open(reportFileName, "a") as reportFile:
                    reportFile.write(elem + ",")
                if "%" in elem:
                    usedSpace = elem.replace("%", "")
                    if int(usedSpace) >= fileSystemthreshold: # Threshold validation
                        with open(reportFileName, "a") as reportFile:
                            reportFile.write("Failed,Threshold of "+str(fileSystemthreshold)+"% exceeded.," + scanType)
                        if(scanType == "Post-cleanup"):
                            errorMessage = "GE FileSystem: " + instanceName + " - physical memory usage exceeds the threshold (" + str(fileSystemthreshold)+ "%)\n"
                            print(errorMessage)
                            saveErrorLogs(errorMessage)
                    else:
                        with open(reportFileName, "a") as reportFile:
                            reportFile.write("Success,-," + scanType)

    if stderrdata:
        with open(reportFileName, "a") as reportFile:
            reportFile.write("-,-,-,-,Failed," + stderrdata.decode('utf-8').strip().replace(",", "-") + "," + scanType)
        errorMessage = "GE FileSystem: " + instanceName + " - " + stderrdata.decode('utf-8').strip() + "\n"
        print(errorMessage)
        saveErrorLogs(errorMessage)
    return status




# GE Queue Monitoring
def queueMonitoring():
    print("\n----------------------- GE Queue Monitoring -------------------------")
    reportFileName = geQueueMonitoringReport # GE_Queue_Monitoring_Report.csv
    archLinux = "lx-amd64" # Default value
    command = "qstat -f | grep ossmsci.q"
    stdoutdata, stderrdata, proc = exProces(command)

    if stdoutdata:
        print(stdoutdata.strip())
        status = True

        # Generate Report File
        header="Queue Name,Queue Type,Resv/Used/Total,Avg. Load,Arch,Queue States,Queue Status,Comments\n"
        with open(reportFileName, "a") as reportFile:
            reportFile.write(header)

        lines=stdoutdata.split("\n")
        for line in lines:
            if line:
                if not line.strip().endswith(archLinux): # Unexpected element queue state
                    queueStatus = "Failed"
                    status = False
                    elems = line.split(archLinux)
                    errorMessage = "GE Queue: Unexpected elem: " + elems[1].strip() + " in Queue \"states\"  \n"
                    print(errorMessage)
                    saveErrorLogs(errorMessage)
                else:
                    queueStatus = "Success"

                data = ""
                elements = line.split() # Fetch queue data
                for elem in elements:
                    data = data + elem + ","

                if queueStatus == "Success":  # Appending queue state and Status
                    data = data + "-" + "," + queueStatus + ",-\n"
                else:
                    data = data + queueStatus + ",Unexpected elem in Queue \"states\" \n"
                with open(reportFileName, "a") as reportFile:
                    reportFile.write(data)

        # Queue Status Check
        if status:
            print("GE Queue Monitoring Check: Success!")
            print("\nResults are saved to " + wsPath + reportFileName)
        else:
            print("GE Queue Monitoring Check: Failed!")
            print("\nResults are saved to " + wsPath + reportFileName)
            print("---------------------------------------------------------------------")
            exit(1)

    if stderrdata:
        errorMessage = "GE Queue: " + stderrdata.decode('utf-8').strip() + "\n"
        print(errorMessage)
        saveErrorLogs(errorMessage)

    print("---------------------------------------------------------------------")




# Docker System Analysis
def dockerSystemAnalysis():
    print("\n---------------------- Docker System Analysis -----------------------")
    for instance in gridEngines:
        status = executeDockerSystemAnalysis(instance)
    print("---------------------------------------------------------------------")

def executeDockerSystemAnalysis(instance):
    instanceName = "seliius" + instance
    reportFileName = geDockerSystemAnalysisReport # InstanceName/InstanceName_Docker_System_Analysis_Report.csv
    reportFileName = reportFileName.replace("InstanceName",instanceName) # seliius26249/seliius26249_Docker_System_Analysis_Report.csv
    print(instanceName + " :")

    dockerCommand = "docker system df"
    command = getTwicCommand(instance) + " ; " + dockerCommand
    stdoutdata, stderrdata, proc = exProces(command)

    if stdoutdata:
        print(stdoutdata.strip() + "\n")
        lines=stdoutdata.strip().split("\n")
        for line in lines:
            if line != "":
                line = line.replace("Local Volumes","Local_Volumes").replace("Build Cache","Build_Cache").replace("TYPE","Type").replace("RECLAIMABLE","Reclaimable").replace("SIZE","Size").replace("ACTIVE","Active").replace("TOTAL","Total")
                data = line.split(" ")
                data[:] = [x for x in data if x]
                temp = ""
                for x in range(5):
                    temp= temp + data[x] + ","
                temp = temp.rstrip(temp[-1]) # Remove extra ,
                with open(reportFileName, "a") as reportFile:
                    reportFile.write(temp)
            with open(reportFileName, "a") as reportFile:
                reportFile.write("\n")
        print("Results are saved to " + wsPath + reportFileName + "\n")

    if stderrdata:
        errorMessage = "GE Docker System Analysis: " + stderrdata.decode('utf-8').strip() + "\n"
        print(errorMessage)
        saveErrorLogs(errorMessage)




# Docker Container Analysis
def dockerContainerAnalysis():
    print("\n---------------------- Docker Container Analysis ---------------------")
    for instance in gridEngines:
        status = executeDockerContainerAnalysis(instance)
    print("----------------------------------------------------------------------\n\n\n\n\n")

def executeDockerContainerAnalysis(instance):
    instanceName = "seliius" + instance
    reportFileName = geDockerContainerAnalysisReport  # InstanceName/InstanceName_Docker_Container_Analysis_Report.csv
    reportFileName = reportFileName.replace("InstanceName",instanceName) # seliius26249/seliius26249_Docker_Container_Analysis_Report.csv
    print(instanceName + " :")

    reportHeader="Container ID,Container Name,Docker Image,Port Number,State,Status,Created At,_Running For,Size\n"
    with open(reportFileName, "a") as reportFile:
        reportFile.write(reportHeader)


    # Lists all 'Running' containers
    dockerCommand = "docker ps --no-trunc --format '{{.ID}}|{{.Names}}|{{.Image}}|{{.Ports}}|Running|{{.Status}}|{{.CreatedAt}}|{{.RunningFor}}|{{.Size}}'"
    command = getTwicCommand(instance) + " ; " + dockerCommand
    stdoutdata_running, stderrdata, proc = exProces(command)

    if stdoutdata_running:
        with open(reportFileName, "a") as reportFile:
            reportFile.write(stdoutdata_running.replace(",","").replace("|",",")) # Remove "," from the port number to preserve the csv template.

    if stderrdata:
        errorMessage = "GE Docker Container Analysis: " + instanceName + " - " + stderrdata.decode('utf-8').strip() + "\n"
        print(errorMessage)
        saveErrorLogs(errorMessage)


    # Lists all 'Exited' containers
    dockerCommand = "docker ps -f 'status=exited' --no-trunc --format '{{.ID}}|{{.Names}}|{{.Image}}|{{.Ports}}|Exited|{{.Status}}|{{.CreatedAt}}|{{.RunningFor}}|{{.Size}}'"
    command = getTwicCommand(instance) + " ; " + dockerCommand
    stdoutdata_exited, stderrdata, proc = exProces(command)

    if stdoutdata_exited:
        with open(reportFileName, "a") as reportFile:
            reportFile.write(stdoutdata_exited.replace(",","").replace("|",","))

    if stderrdata:
        errorMessage = "GE Docker Container Analysis: " + instanceName + " - " + stderrdata.decode('utf-8').strip() + "\n"
        print(errorMessage)
        saveErrorLogs(errorMessage)


    # Handling Empty List
    if stdoutdata_running == "" and stdoutdata_exited == "":
        with open(reportFileName, "a") as reportFile:
            reportFile.write("No Containers Available!,,,,,,,,")
        print(instanceName + " - No Containers Available!\n")
    else:
        print(instanceName + " - Results are saved to " + wsPath + reportFileName + "\n")




# Docker Container Cleanup
def dockerContainerCleanup():
    print("\n---------------------- Docker Container Cleanup ---------------------")
    for instance in gridEngines:
        status = executeDockerContainerCleanup(instance)
    print("---------------------------------------------------------------------")

def executeDockerContainerCleanup(instance):
    instanceName = "seliius" + instance
    reportFileName = geDockerContainerCleanupReport # InstanceName/InstanceName_Docker_Container_Cleanup_Report.txt
    reportFileName = reportFileName.replace("InstanceName",instanceName) # seliius26249/seliius26249_Docker_Container_Cleanup_Report.txt
    print(instanceName + ":")

    # Remove all 'Running' containers
    removeAllRunningContainers = os.environ['REMOVE_ALL_RUNNING_CONTAINERS']
    if(removeAllRunningContainers == "true"):
        print(instanceName + ": Stopping and removing all running containers!")

        # Check if there are any 'Running' containers
        containerExists = False
        dockerCommand = "docker ps -q"
        command = getTwicCommand(instance) + " ; " + dockerCommand
        stdoutdata, stderrdata, proc = exProces(command)
        if stdoutdata:
            containerExists = True

        # Remove the 'Running' containers
        if (containerExists):
            dockerCommand = "docker kill $(docker ps -q);docker rm $(docker ps -a -q);"
            command = getTwicCommand(instance) + " ; " + dockerCommand
            stdoutdata, stderrdata, proc = exProces(command)

            if stdoutdata:
                print(stdoutdata.strip() + "\n")
                with open(reportFileName, "a") as reportFile:
                    reportFile.write(stdoutdata)

            if stderrdata:
                errorMessage = "GE Docker Container Cleanup: " + instanceName + " - "  + stderrdata.decode('utf-8').strip().replace("\n"," | ") + "\n"
                print(errorMessage)
                saveErrorLogs(errorMessage)
        else:
            print(instanceName + ": No running containers available!")

    # Remove all 'Exited' containers
    print(instanceName + ": Removing all exited containers!")

    dockerCommand = "docker container prune --force"
    command = getTwicCommand(instance) + " ; " + dockerCommand
    stdoutdata, stderrdata, proc = exProces(command)

    if stdoutdata:
        print(stdoutdata.strip() + "\n")
        with open(reportFileName, "a") as reportFile:
            reportFile.write(stdoutdata)
        print("Results are saved to " + wsPath + reportFileName + "\n")

    if stderrdata:
        errorMessage = "GE Docker Container Cleanup: " + instanceName + " - "  + stderrdata.decode('utf-8').strip() + "\n"
        print(errorMessage)
        saveErrorLogs(errorMessage)




# Docker Image Analysis
def dockerImageAnalysis():
    print("\n---------------------- Docker Image Analysis ---------------------")
    for instance in gridEngines:
        status = executeDockerImageAnalysis(instance)
    print("------------------------------------------------------------------\n\n\n\n\n")


def executeDockerImageAnalysis(instance):
    instanceName = "seliius" + instance
    reportFileName = geDockerImageAnalysisReport # InstanceName/InstanceName_Docker_Image_Analysis_Report.csv
    reportFileName = reportFileName.replace("InstanceName",instanceName) # seliius26249/seliius26249_Docker_Image_Analysis_Report.csv
    print(instanceName + ":")

    reportHeader="Repository,Tag,Image ID,Created,Size,Category\n"
    with open(reportFileName, "a") as reportFile:
        reportFile.write(reportHeader)


    # List all 'Unused' Images
    dockerCommand = "runningImages=$(docker ps --format {{.Image}});docker images --no-trunc --format {{.Repository}},{{.Tag}},{{.ID}},{{.CreatedAt}},{{.Size}},Unused | grep -v '$runningImages'"
    command = getTwicCommand(instance) + " ; " + dockerCommand
    stdoutdata_unused, stderrdata, proc = exProces(command)

    if stdoutdata_unused:
        with open(reportFileName, "a") as reportFile:
            reportFile.write(stdoutdata_unused)

    if stderrdata:
        errorMessage = "GE Docker Image Analysis: " + instanceName + " - " + stderrdata.decode('utf-8').strip() + "\n"
        print(errorMessage)
        saveErrorLogs(errorMessage)


    # List all 'Used' Images
    dockerCommand = "runningImages=$(docker ps --format {{.Image}});docker images --no-trunc --format {{.Repository}},{{.Tag}},{{.ID}},{{.CreatedAt}},{{.Size}},In-Use | grep '$runningImages'"
    command = getTwicCommand(instance) + " ; " + dockerCommand
    stdoutdata_used, stderrdata, proc = exProces(command)

    if stdoutdata_used:
        with open(reportFileName, "a") as reportFile:
            reportFile.write(stdoutdata_used)

    if stderrdata:
        errorMessage = "GE Docker Image Analysis: " + instanceName + " - " + stderrdata.decode('utf-8').strip() + "\n"
        print(errorMessage)
        saveErrorLogs(errorMessage)


    # List all 'Dangling' Images
    dockerCommand = "docker images --filter 'dangling=true' --no-trunc --format {{.Repository}},{{.Tag}},{{.ID}},{{.CreatedAt}},{{.Size}},Dangling"
    command = getTwicCommand(instance) + " ; " + dockerCommand
    stdoutdata_dangling, stderrdata, proc = exProces(command)

    if stdoutdata_dangling:
        with open(reportFileName, "a") as reportFile:
            reportFile.write(stdoutdata_dangling)

    if stderrdata:
        errorMessage = "GE Docker Image Analysis: " + instanceName + " - " + stderrdata.decode('utf-8').strip() + "\n"
        print(errorMessage)
        saveErrorLogs(errorMessage)


    # Handling Empty List
    if stdoutdata_unused == "" and stdoutdata_used == "" and stdoutdata_dangling == "":
        with open(reportFileName, "a") as reportFile:
            reportFile.write("No Images Available!,,,,,")
        print(instanceName + " - No Images Available!\n")
    else:
        print(instanceName + " - Results are saved to " + wsPath + reportFileName + "\n")




# Docker Image Cleanup
def dockerImageCleanup():
    print("\n---------------------- Docker Image Cleanup ---------------------")
    for instance in gridEngines:
        status = executeDockerImageCleanup(instance)
    print("-----------------------------------------------------------------")


def executeDockerImageCleanup(instance):
    instanceName = "seliius" + instance
    reportFileName = geDockerImageCleanupReport # InstanceName/InstanceName_Docker_Image_Cleanup_Report.txt
    reportFileName = reportFileName.replace("InstanceName",instanceName) # seliius26249/seliius26249_Docker_Image_Cleanup_Report.txt
    print(instanceName + ":")

    dockerCommand = "docker image prune --all --force" # Removes all unused and dangling images
    command = getTwicCommand(instance) + " ; " + dockerCommand
    stdoutdata, stderrdata, proc = exProces(command)

    if stdoutdata:
        print(stdoutdata.strip() + "\n")
        with open(reportFileName, "a") as reportFile:
            reportFile.write(stdoutdata)
        print("Results are saved to " + wsPath + reportFileName + "\n")

    if stderrdata:
        errorMessage = "GE Docker Image Cleanup: " + instanceName + " - " + stderrdata.decode('utf-8').strip() + "\n"
        print(errorMessage)
        saveErrorLogs(errorMessage)




# Docker Volume Cleanup
def dockerVolumeCleanup():
    print("\n---------------------- Docker Volume Cleanup ---------------------")
    for instance in gridEngines:
        status = executeDockerVolumeCleanup(instance)
    print("-----------------------------------------------------------------")


def executeDockerVolumeCleanup(instance):
    instanceName = "seliius" + instance
    reportFileName = geDockerVolumeCleanupReport # InstanceName/InstanceName_Docker_Volume_Cleanup_Report.txt
    reportFileName = reportFileName.replace("InstanceName",instanceName) # seliius26249/seliius26249_Docker_Volume_Cleanup_Report.txt
    print(instanceName + ":")

    dockerCommand = "docker volume prune --force" # Removes all unused local volumes
    command = getTwicCommand(instance) + " ; " + dockerCommand
    stdoutdata, stderrdata, proc = exProces(command)

    if stdoutdata:
        print(stdoutdata.strip() + "\n")
        with open(reportFileName, "a") as reportFile:
            reportFile.write(stdoutdata)
        print("Results are saved to " + wsPath + reportFileName + "\n")

    if stderrdata:
        errorMessage = "GE Docker Volume Cleanup: " + instanceName + " - " + stderrdata.decode('utf-8').strip() + "\n"
        print(errorMessage)
        saveErrorLogs(errorMessage)




# Docker Network Cleanup
def dockerNetworkCleanup():
    print("\n-------------------- Docker Network Cleanup ----------------------")
    for instance in gridEngines:
        status = executeDockerNetworkCleanup(instance)
    print("-----------------------------------------------------------------")


def executeDockerNetworkCleanup(instance):
    instanceName = "seliius" + instance
    reportFileName = geDockerNetworkCleanupReport # InstanceName/InstanceName_Docker_Network_Cleanup_Report.txt
    reportFileName = reportFileName.replace("InstanceName",instanceName) # seliius26249/seliius26249_Docker_Network_Cleanup_Report.txt
    print(instanceName + ":")

    dockerCommand = "docker network prune --force" # Removes all unused networks
    command = getTwicCommand(instance) + " ; " + dockerCommand
    stdoutdata, stderrdata, proc = exProces(command)

    if stdoutdata:
        print(stdoutdata.strip() + "\n")
        with open(reportFileName, "a") as reportFile:
            reportFile.write(stdoutdata)
        print("Results are saved to " + wsPath + reportFileName + "\n")

    if stderrdata:
        errorMessage = "GE Docker Network Cleanup: " + instanceName + " - " + stderrdata.decode('utf-8').strip() + "\n"
        print(errorMessage)
        saveErrorLogs(errorMessage)




# Docker Build Cache Cleanup
def dockerCacheCleanup():
    print("\n-------------------- Docker Build Cache Cleanup ----------------------")
    for instance in gridEngines:
        status = executeDockerCacheCleanup(instance)
    print("-----------------------------------------------------------------------")


def executeDockerCacheCleanup(instance):
    instanceName = "seliius" + instance
    reportFileName = geDockerBuildCacheCleanupReport # InstanceName/InstanceName_Docker_Build_Cache_Cleanup_Report.txt
    reportFileName = reportFileName.replace("InstanceName",instanceName) # seliius26249/seliius26249_Docker_Build_Cache_Cleanup_Report.txt
    print(instanceName + ":")

    dockerCommand = "docker builder prune --all --force" # Removes unused build cache.
    command = getTwicCommand(instance) + " ; " + dockerCommand
    stdoutdata, stderrdata, proc = exProces(command)

    if stdoutdata:
        print(stdoutdata.strip() + "\n")
        with open(reportFileName, "a") as reportFile:
            reportFile.write(stdoutdata)
        print("Results are saved to " + wsPath + reportFileName + "\n")

    if stderrdata:
        errorMessage = "GE Docker Build Cache Cleanup: " + instanceName + " - " + stderrdata.decode('utf-8').strip() + "\n"
        print(errorMessage)
        saveErrorLogs(errorMessage)



# Consolidated Report Generation
def generateReport():
    reportFileName = consolidatedReport # GE_Monitoring_Report.html

    # Initialization
    header = "<html><head><style>body {font-family: arial, sans-serif;}table { border-collapse: collapse;font-family: arial, sans-serif;}td, th { text-align: left;border: 1px solid black;padding: 8px;}</style></head><body><b>GE Monitoring - Consolidated Report</b><p>Report Generated: _datetime_</p><br>"
    header = header.replace("_datetime_", datetime.now().strftime("%B %d, %Y %H:%M"))
    with open(reportFileName, "a") as reportFile:
        reportFile.write(header)
    addHorizontalLine()
    with open(reportFileName, "a") as reportFile:
        reportFile.write("<br><p><b>FEM Monitoring Tasks</b></p>")


    # FEM Connection
    env_status = os.environ['FEM_CONNECTION']
    if(env_status == "true"):
        header = "<br><b>FEM Connection:</b><br><br>"
        with open(reportFileName, "a") as reportFile:
            reportFile.write(header)
        createHTMLTable(femConnectionReport)


    # FEM FileSystem
    env_status = os.environ['FEM_FILESYSTEM']
    if(env_status == "true"):
        header = "<br><br><b>FEM FileSystem:</b><br><br>"
        with open(reportFileName, "a") as reportFile:
            reportFile.write(header)
        createHTMLTable(femFileSystemReportPreCleanup)
        createHTMLTable(femFileSystemReport)


    # FEM Password
    header = "<br><br><b>FEM Password:</b><br>"
    message = "<p>Password Check Status: Failed!</p><br>"

    if(passwordCheck): # Global Variable
        message = "<p>Password Check Status: Success!</p><br>"

    with open(reportFileName, "a") as reportFile:
        reportFile.write(header)
        reportFile.write(message)
    addHorizontalLine()


    # GE Instance Metadata
    metadata = "<br><b>GE Instances:</b><br><br><p>For more info on the GE Instances, please refer to <a href = \'https://eteamspace.internal.ericsson.com/x/kBZke\'> E2C Eiffel216 inventory</a></p>"
    with open(reportFileName, "a") as reportFile:
        reportFile.write("<br><p><b>GE Monitoring Tasks</b></p>")
        reportFile.write(metadata)


    # GE Connection
    env_status = os.environ['GE_CONNECTION']
    if(env_status == "true"):
        header = "<br><br><b>GE Connection:</b><br><br>"
        with open(reportFileName, "a") as reportFile:
            reportFile.write(header)
        createHTMLTable(geConnectionReport)


    # GE FileSystem
    env_status = os.environ['GE_FILESYSTEM']
    if(env_status == "true"):
        header = "<br><br><b>GE FileSystem:</b><br><br>"
        with open(reportFileName, "a") as reportFile:
            reportFile.write(header)
        createHTMLTable(geFileSystemReportPreCleanup)
        createHTMLTable(geFileSystemReport)


    # GE Queue Monitoring
    header = "<br><br><b>GE Queue Monitoring:</b><br><br>"
    with open(reportFileName, "a") as reportFile:
        reportFile.write(header)
    createHTMLTable(geQueueMonitoringReport)
    addHorizontalLine()


    # Docker Header
    with open(reportFileName, "a") as reportFile:
        reportFile.write("<br><p><b>Docker Analysis and Cleanup Tasks</b></p>")


    # Docker System Analysis
    env_status = os.environ['GE_DOCKER_ANALYSIS']
    if(env_status == "true"):
        header = "<br><b>Docker System Analysis:</b><br><br>"
        with open(reportFileName, "a") as reportFile:
            reportFile.write(header)

        for instance in gridEngines:
            instanceName = "seliius" + instance
            sub_header = "<br><b>InstanceName</b><br><br>"
            sub_header = sub_header.replace("InstanceName",instanceName)
            with open(reportFileName, "a") as reportFile:
                reportFile.write(sub_header)

            outputFile = geDockerSystemAnalysisReport.replace("InstanceName",instanceName)
            if(exists(outputFile)):
                createHTMLTable(outputFile)
        addHorizontalLine()


    # Docker Container Analysis
    env_status = os.environ['GE_DOCKER_CONTAINER']
    if(env_status == "true"):
        header = "<br><br><b>Docker Container Analysis:</b><br><br>"
        with open(reportFileName, "a") as reportFile:
            reportFile.write(header)

        for instance in gridEngines:
            instanceName = "seliius" + instance
            sub_header = "<br><b>InstanceName</b><br><br>"
            sub_header = sub_header.replace("InstanceName",instanceName)
            with open(reportFileName, "a") as reportFile:
                reportFile.write(sub_header)

            outputFile = geDockerContainerAnalysisReport.replace("InstanceName",instanceName)
            if(exists(outputFile)):
                createHTMLTable(outputFile)
        addHorizontalLine()


    # Docker Container Cleanup
    env_status = os.environ['GE_DOCKER_CONTAINER']
    if(env_status == "true"):
        header = "<br><br><b>Docker Container Cleanup:</b><br><br>"
        with open(reportFileName, "a") as reportFile:
            reportFile.write(header)

        for instance in gridEngines:
            instanceName = "seliius" + instance
            sub_header = "<br><b>InstanceName</b><br><br>"
            sub_header = sub_header.replace("InstanceName",instanceName)
            with open(reportFileName, "a") as reportFile:
                reportFile.write(sub_header)

            outputFile = geDockerContainerCleanupReport.replace("InstanceName",instanceName)
            if(exists(outputFile)):
                createHTMLString(outputFile)
        addHorizontalLine()


    # Docker Image Analysis
    env_status = os.environ['GE_DOCKER_IMAGE']
    if(env_status == "true"):
        header = "<br><br><b>Docker Image Analysis:</b><br><br>"
        with open(reportFileName, "a") as reportFile:
            reportFile.write(header)

        for instance in gridEngines:
            instanceName = "seliius" + instance
            sub_header = "<br><b>InstanceName</b><br><br>"
            sub_header = sub_header.replace("InstanceName",instanceName)
            with open(reportFileName, "a") as reportFile:
                reportFile.write(sub_header)

            outputFile = geDockerImageAnalysisReport.replace("InstanceName",instanceName)
            if(exists(outputFile)):
                createHTMLTable(outputFile)
        addHorizontalLine()


    # Docker Image Cleanup
    env_status = os.environ['GE_DOCKER_IMAGE']
    if(env_status == "true"):
        header = "<br><br><b>Docker Image Cleanup:</b><br><br>"
        with open(reportFileName, "a") as reportFile:
            reportFile.write(header)

        for instance in gridEngines:
            instanceName = "seliius" + instance
            sub_header = "<br><b>InstanceName</b><br><br>"
            sub_header = sub_header.replace("InstanceName",instanceName)
            with open(reportFileName, "a") as reportFile:
                reportFile.write(sub_header)

            outputFile = geDockerImageCleanupReport.replace("InstanceName",instanceName)
            if(exists(outputFile)):
                createHTMLString(outputFile)
        addHorizontalLine()


    # Docker Volume Cleanup
    env_status = os.environ['GE_DOCKER_VOLUME']
    if(env_status == "true"):
        header = "<br><br><b>Docker Volume Cleanup:</b><br><br>"
        with open(reportFileName, "a") as reportFile:
            reportFile.write(header)

        for instance in gridEngines:
            instanceName = "seliius" + instance
            sub_header = "<br><b>InstanceName</b><br><br>"
            sub_header = sub_header.replace("InstanceName",instanceName)
            with open(reportFileName, "a") as reportFile:
                reportFile.write(sub_header)

            outputFile = geDockerVolumeCleanupReport.replace("InstanceName",instanceName)
            if(exists(outputFile)):
                createHTMLString(outputFile)
        addHorizontalLine()


    # Docker Network Cleanup
    env_status = os.environ['GE_DOCKER_NETWORK']
    if(env_status == "true"):
        header = "<br><br><b>Docker Network Cleanup:</b><br><br>"
        with open(reportFileName, "a") as reportFile:
            reportFile.write(header)

        for instance in gridEngines:
            instanceName = "seliius" + instance
            sub_header = "<br><b>InstanceName</b><br><br>"
            sub_header = sub_header.replace("InstanceName",instanceName)
            with open(reportFileName, "a") as reportFile:
                reportFile.write(sub_header)

            outputFile = geDockerNetworkCleanupReport.replace("InstanceName",instanceName)
            if(exists(outputFile)):
                createHTMLString(outputFile)
        addHorizontalLine()


    # Docker Build Cache Cleanup
    env_status = os.environ['GE_DOCKER_BUILD_CACHE']
    if(env_status == "true"):
        header = "<br><br><b>Docker Build Cache Cleanup:</b><br><br>"
        with open(reportFileName, "a") as reportFile:
            reportFile.write(header)

        for instance in gridEngines:
            instanceName = "seliius" + instance
            sub_header = "<br><b>InstanceName</b><br><br>"
            sub_header = sub_header.replace("InstanceName",instanceName)
            with open(reportFileName, "a") as reportFile:
                reportFile.write(sub_header)

            outputFile = geDockerBuildCacheCleanupReport.replace("InstanceName",instanceName)
            if(exists(outputFile)):
                createHTMLString(outputFile)
        addHorizontalLine()

    print("Results are saved to " + wsPath + reportFileName + "\n")




# Send Email Notification
def email():
    print("\n---------------------- Email Notification ----------------------------")
    if path.exists(errorFileName):
        if os.stat(errorFileName).st_size != 0:
            print("GE Monitoring issues have been recorded in " + wsPath + errorFileName)
            createEmail()
            command = """( echo To: """ + MAIL + """
                echo From: """ + senderEmail + """
                echo "Content-Type: text/html; "
                echo Subject: "GE Monitoring - ISSUES detected!"
                cat """ + emailFileName + """ ) | sendmail -t"""
            stdoutdata, stderrdata, proc = exProces(command)
            print("An email has been sent to " + MAIL)
    else:
        print("No issues have been recorded!")
    print("----------------------------------------------------------------------")


def createEmail():
    job_name=JOB_URL.rsplit('/')[-2]
    emailText = """<html>
    <head>
    <style>
        html, body { margin: 0 auto !important; padding: 0 !important; height: 100% !important; width: 100% !important;
        background:#fff;font-family: Arial,sans-serif;color: #333;  }
        * {-ms-text-size-adjust: 100%;}
    </style>
    </head>
    <body width="100%" style="margin: 0; padding: 0 !important; mso-line-height-rule: exactly;">
        <div style="text-align:center; background-color:rgb(255,140,10); color:#fff; ">
            <br><h2><i>"Connection, Space, Queue or Docker config file issue with GE agent(s) detected."</i></h2><br>
        </div>
        <div><br><br><i>"""

    with open(emailFileName, "w") as emailContent:
        emailContent.write(emailText)
        with open(errorFileName, "r") as errorFile:
            for line in errorFile.readlines():
                emailContent.write(line + """<br>""")
        emailContent.write("""</i><br><br><p><i>This mail was sent automatically from the Jenkins job <a href=""" + JOB_URL + BUILD_NUMBER + """>""" + job_name + """</a></i></p><i>""")
        emailContent.write(datetime.now().strftime("%B %d, %Y %H:%M") + "</i></p>")
        emailContent.write("</div></body></html>")

# Cleanup /proj/mvn directory
def mavenDirectoryCleanup():
    print("\n------------------------------ Maven Directory Cleanup -----------------------------")

    # Pre-cleanup
    print("Pre-cleanup:")
    command = "df -h /proj/mvn"
    stdoutdata, stderrdata, proc = exProces(command)

    if stdoutdata:
        print(stdoutdata.strip())

    if stderrdata:
        errorMessage = "Maven Directory Cleanup: " + command + " - " + stderrdata.decode('utf-8').strip() + "\n"
        print(errorMessage)
        saveErrorLogs(errorMessage)

    # Cleanup
    command = "cd /proj/mvn/.m2/repository/ && rm -rf *"
    stdoutdata, stderrdata, proc = exProces(command)

    if stdoutdata:
        print(stdoutdata.strip())

    if stderrdata:
        errorMessage = "Maven Directory Cleanup: " + command + " - " + stderrdata.decode('utf-8').strip() + "\n"
        print(errorMessage)
        saveErrorLogs(errorMessage)

    # Post-cleanup
    print("\nPost-cleanup:")
    command = "df -h /proj/mvn"
    stdoutdata, stderrdata, proc = exProces(command)

    if stdoutdata:
        print(stdoutdata.strip())

    if stderrdata:
        errorMessage = "Maven Directory Cleanup: " + command + " - " + stderrdata.decode('utf-8').strip() + "\n"
        print(errorMessage)
        saveErrorLogs(errorMessage)

    print("------------------------------------------------------------------------------------\n\n\n\n\n")


# GE Workspace Cleanup
def gridEngineWorkspaceCleanup():
    print("\n---------------------- GE Workspace Cleanup ---------------------")

    # Pre-cleanup
    print("Pre-cleanup:")
    for instance in femInstancesWorkspaceCleanup:
        directory = "/proj/eiffel216_config_instance".replace("instance", instance)
        command = "df -h " + directory
        stdoutdata, stderrdata, proc = exProces(command)

        if stdoutdata:
            print(stdoutdata.strip())

        if stderrdata:
            errorMessage = "GE Workspace Cleanup: " + command + " - " + stderrdata + "\n"
            saveErrorLogs(errorMessage)

    # Cleanup
    job_name=JOB_URL.rsplit('/')[-2]

    for instance in femInstancesWorkspaceCleanup:
        directory = "/proj/eiffel216_config_instance".replace("instance", instance)
        command = "cd " + directory + "/agents/ && ls"
        stdoutdata, stderrdata, proc = exProces(command)

        if stdoutdata:
            for agent in stdoutdata.strip().split("\n"):
                if agent:
                    command = "cd "+ directory + "/agents/" + agent + "/workspace && ls -a"
                    stdoutdata, stderrdata, proc = exProces(command)

                    if stdoutdata:
                        for folder in stdoutdata.strip().split("\n"):
                            if not re.search(job_name, folder) and folder != "." and folder != "..":
                                command = "cd "+ directory + "/agents/" + agent + "/workspace/ && rm -rf " +folder
                                # command: cd /proj/eiffel216_config_fem1s11/agents/RHEL7_GE_Docker_4/workspace/ && rm -rf eric-oss-architecture-docs_PreCodeReview
                                stdoutdata, stderrdata, proc = exProces(command)

                                if stderrdata:
                                    errorMessage = "GE Workspace Cleanup: " + command + " - " + stderrdata + "\n"
                                    saveErrorLogs(errorMessage)

                    if stderrdata:
                        errorMessage = "GE Workspace Cleanup: " + command + " - " + stderrdata + "\n"
                        saveErrorLogs(errorMessage)

        if stderrdata:
            errorMessage = "GE Workspace Cleanup: " + command + " - " + stderrdata + "\n"
            saveErrorLogs(errorMessage)

    # Post-cleanup
    print("Post-cleanup:")
    for instance in femInstancesWorkspaceCleanup:
        directory = "/proj/eiffel216_config_instance".replace("instance", instance)
        command = "df -h " + directory
        stdoutdata, stderrdata, proc = exProces(command)

        if stdoutdata:
            print(stdoutdata.strip())

        if stderrdata:
            errorMessage = "GE Workspace Cleanup: " + command + " - " + stderrdata + "\n"
            saveErrorLogs(errorMessage)

    print("-----------------------------------------------------------------\n\n\n\n\n")




# Function Call Redirections
def main():
    if len(sys.argv) !=2:
        print("Error: Function name not supplied!")
        exit()

    functionName=sys.argv[1]

    if functionName == "Prepare":
        prepareWorkspace()
    elif functionName == "FEM_Connection":
        femConnection()
    elif functionName == "FEM_FileSystem":
        femFileSystem()
    elif functionName == "FEM_Password":
        mypasswdExist()
    elif functionName == "GE_Connection":
        connection()
    elif functionName == "GE_FileSystem":
        fileSystem('Pre-cleanup')
    elif functionName == "GE_Queue":
        queueMonitoring()
    elif functionName == "GE_DockerSystemAnalysis":
        dockerSystemAnalysis()
    elif functionName == "GE_DockerContainer":
        dockerContainerAnalysis()
        dockerContainerCleanup()
    elif functionName == "GE_DockerImage":
        dockerImageAnalysis()
        dockerImageCleanup()
    elif functionName == "GE_DockerVolume":
        dockerVolumeCleanup()
    elif functionName == "GE_DockerNetwork":
        dockerNetworkCleanup()
    elif functionName == "GE_DockerCache":
        dockerCacheCleanup()
    elif functionName == "PostCleanupCheck":
        fileSystem("Post-cleanup")
    elif functionName == "GenerateReport":
        generateReport()
    elif functionName == "Email":
        email()
    elif functionName == "MavenDirectory":
        mavenDirectoryCleanup()
    elif functionName == "GEWorkspace":
        gridEngineWorkspaceCleanup()


# Main function
if __name__ == '__main__':
    main()
