#!/usr/bin/python3
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
import os
import re
import sys
import os.path
import requests
import subprocess
from datetime import date
from datetime import datetime


# Variables
# HTTP Request
username = os.environ.get("GERRIT_USERNAME")
password = os.environ.get("GERRIT_PASSWORD")

# DR Exemption Requests
designRuleExemptionData = []
designRuleExemptionData_Expired = []
designRuleExemptionData_SoonToBe_Expired = []

# Report Generation
report = os.environ.get("REPORT")
reportHeader = "Exemption Status,JIRA Key,JIRA Status,JIRA Resolution,Exempt DR Tag,Helm Chart Name,Planned Expiration Date,Days Until Planned Expiration Date,Email Distribution List,Reporter,Reporter Email,Assignee,Assignee Email,JIRA Type\n"


# Functions
# Execute Shell
def executeShell(command):
    subprocess.call(command, shell=True)


# Validate ODP DR Exemption Requests
def validateDesignRuleExemptions():
    fetchDesignRuleExemptions()
    categorizeDesignRuleExemptions()
    generateReport()
    sendEmailNotification()
    removeExpiredDesignRuleExemptions()


# Fetch ODP Approved DR Exemption Requests from JIRA Board
def fetchDesignRuleExemptions():
    global designRuleExemptionData

    # HTTP Request - Support Ticket
    url = "https://eteamproject.internal.ericsson.com/rest/api/2/search?jql=Project = IDUN AND Type = Support AND labels in (OdpDrExemptionRequest, OdpDrExemptionGranted) AND Key != 'IDUN-90863'"
    response = requests.get(url, auth=(username, password))
    if response.status_code == 200:
        results = response.json()
    else:
        errorMessageTemplate = "[Error]: HTTP Request to the ODP JIRA Board returned the status code - {status_code}!"
        errorMessage = errorMessageTemplate.format(status_code=str(response.status_code))
        sys.exit(errorMessage)

    # HTTP Response
    if results:
        for value in results["issues"]:

            # DR Exemption Request JIRA Information
            jiraReporterName = "Unassigned"
            jiraAssigneeName = "Unassigned"
            jiraReporterEmail = "Unassigned"
            jiraAssigneeEmail = "Unassigned"
            jiraResolution = "Unresolved"
            jiraType = "Support"

            jiraKey = str(value["key"])
            jiraStatus = str(value["fields"]["status"]["name"])

            if str(value["fields"]["resolution"]) != "None":
                jiraResolution = str(value["fields"]["resolution"]["name"])

            if str(value["fields"]["reporter"]) != "None":
                jiraReporterName = (value["fields"]["reporter"]["displayName"]).encode("utf-8")
                jiraReporterEmail = (value["fields"]["reporter"]["emailAddress"]).encode("utf-8")

            if str(value["fields"]["assignee"]) != "None":
                jiraAssigneeName = (value["fields"]["assignee"]["displayName"]).encode("utf-8")
                jiraAssigneeEmail = (value["fields"]["assignee"]["emailAddress"]).encode("utf-8")

            # DR Exemption Data
            jiraDesignRuleTag = str(value["fields"]["customfield_31712"])
            jiraHelmChartName = str(value["fields"]["customfield_50811"])
            jiraPlannedExpirationDate = str(value["fields"]["customfield_42419"])
            jiraEmailDistributionList = str(value["fields"]["customfield_42115"])

            # Handling Multiple values
            defaultValue = "<Please complete>"

            if jiraHelmChartName != defaultValue:
                jiraHelmChartName = jiraHelmChartName.replace(",", ";").replace(" ", "")
            if jiraDesignRuleTag != defaultValue:
                jiraDesignRuleTag = jiraDesignRuleTag.replace(",", ";").replace(" ", "")
            if jiraEmailDistributionList != defaultValue:
                jiraEmailDistributionList = jiraEmailDistributionList.replace(",", ";").replace(" ", "")

            # Exemption Status + Days until Expiration Date
            jiraExemptionStatus = "Valid"
            jiraDaysUntilPlannedExpirationDate = "None"

            if jiraPlannedExpirationDate != "None":
                jiraDaysUntilPlannedExpirationDate = str(((datetime.strptime(jiraPlannedExpirationDate, "%Y-%m-%d").date()) - (date.today())).days)

                if int(jiraDaysUntilPlannedExpirationDate) <= 0:
                    if jiraStatus == "Approved":
                        jiraExemptionStatus = "Expired"
                    elif jiraStatus == "Closed":
                        jiraExemptionStatus = "Expired & Closed"
                elif (int(jiraDaysUntilPlannedExpirationDate) <= 7 and int(jiraDaysUntilPlannedExpirationDate) > 0):
                    jiraExemptionStatus = "Soon to be Expired"

                if int(jiraDaysUntilPlannedExpirationDate) < 0:
                    jiraDaysUntilPlannedExpirationDate = "-1"

                if int(jiraDaysUntilPlannedExpirationDate) > 0:
                    if jiraStatus == "Closed":
                        jiraExemptionStatus = "Closed"

            # DR Exemption Data List
            dataTemplate = "{jira_exemption_status},{jira_key},{jira_status},{jira_resolution},{jira_design_rule_tag},{jira_helm_chart_name},{jira_planned_expiration_date},{jira_days_until_planned_expiration_date},{jira_email_distribution_list},{jira_reporter_name},{jira_reporter_email},{jira_assignee_name},{jira_assignee_email},{jira_type}\n"
            dataString = dataTemplate.format(
                jira_exemption_status=jiraExemptionStatus,
                jira_key=jiraKey,
                jira_status=jiraStatus,
                jira_resolution=jiraResolution,
                jira_design_rule_tag=jiraDesignRuleTag,
                jira_helm_chart_name=jiraHelmChartName,
                jira_planned_expiration_date=jiraPlannedExpirationDate,
                jira_days_until_planned_expiration_date=jiraDaysUntilPlannedExpirationDate,
                jira_email_distribution_list=jiraEmailDistributionList,
                jira_reporter_name=jiraReporterName,
                jira_reporter_email=jiraReporterEmail,
                jira_assignee_name=jiraAssigneeName,
                jira_assignee_email=jiraAssigneeEmail,
                jira_type=jiraType
            )

            designRuleExemptionData.append(dataString.split(","))

            # Data Arrangement
            # 0 -> Exemption Status
            # 1 -> JIRA Key
            # 2 -> JIRA Status
            # 3 -> JIRA Resolution
            # 4 -> Exempt DR Tag
            # 5 -> Helm Chart Name
            # 6 -> Planned Expiration Date
            # 7 -> Days Until Planned Expiration Date
            # 8 -> Email Distribution List
            # 9 -> Reporter Name
            # 10 -> Reporter Email
            # 11 -> Assignee Name
            # 12 -> Assignee Email
            # 13 -> JIRA Type


    # HTTP Request - Exemption Request
    url = "https://eteamproject.internal.ericsson.com/rest/api/2/search?jql=Project = IDUN AND Type = 'Exemption Request' AND labels in (ODP, OdpDrExemptionRequest, OdpDrExemptionGranted)"
    response = requests.get(url, auth=(username, password))
    if response.status_code == 200:
        results = response.json()
    else:
        errorMessageTemplate = "[Error]: HTTP Request to the ODP JIRA Board returned the status code - {status_code}!"
        errorMessage = errorMessageTemplate.format(status_code=str(response.status_code))
        sys.exit(errorMessage)

    # HTTP Response
    if results:
        for value in results["issues"]:

            # DR Exemption Request JIRA Information
            jiraReporterName = "Unassigned"
            jiraAssigneeName = "Unassigned"
            jiraReporterEmail = "Unassigned"
            jiraAssigneeEmail = "Unassigned"
            jiraResolution = "Unresolved"
            jiraType = "Exemption Request"

            jiraKey = str(value["key"])
            jiraStatus = str(value["fields"]["status"]["name"])

            if str(value["fields"]["resolution"]) != "None":
                jiraResolution = str(value["fields"]["resolution"]["name"])

            if str(value["fields"]["reporter"]) != "None":
                jiraReporterName = (value["fields"]["reporter"]["displayName"]).encode("utf-8")
                jiraReporterEmail = (value["fields"]["reporter"]["emailAddress"]).encode("utf-8")

            if str(value["fields"]["assignee"]) != "None":
                jiraAssigneeName = (value["fields"]["assignee"]["displayName"]).encode("utf-8")
                jiraAssigneeEmail = (value["fields"]["assignee"]["emailAddress"]).encode("utf-8")

            # DR Exemption Data
            jiraDesignRuleTag = str(value["fields"]["customfield_31712"])
            jiraHelmChartName = str(value["fields"]["customfield_50811"])
            jiraPlannedExpirationDate = str(value["fields"]["customfield_42419"])
            jiraEmailDistributionList = str(value["fields"]["customfield_42115"])

            # Handling Multiple values
            defaultValue = "<Please complete>"

            if jiraHelmChartName != defaultValue:
                jiraHelmChartName = jiraHelmChartName.replace(",", ";").replace(" ", "")
            if jiraDesignRuleTag != defaultValue:
                jiraDesignRuleTag = jiraDesignRuleTag.replace(",", ";").replace(" ", "")
            if jiraEmailDistributionList != defaultValue:
                jiraEmailDistributionList = jiraEmailDistributionList.replace(",", ";").replace(" ", "")

            # Exemption Status + Days until Expiration Date
            jiraExemptionStatus = "Valid"
            jiraDaysUntilPlannedExpirationDate = "None"

            if jiraPlannedExpirationDate != "None":
                jiraDaysUntilPlannedExpirationDate = str(((datetime.strptime(jiraPlannedExpirationDate, "%Y-%m-%d").date()) - (date.today())).days)

                if int(jiraDaysUntilPlannedExpirationDate) <= 0:
                    if jiraStatus == "Approved":
                        jiraExemptionStatus = "Expired"
                    elif jiraStatus == "Closed":
                        jiraExemptionStatus = "Expired & Closed"
                elif (int(jiraDaysUntilPlannedExpirationDate) <= 7 and int(jiraDaysUntilPlannedExpirationDate) > 0):
                    jiraExemptionStatus = "Soon to be Expired"

                if int(jiraDaysUntilPlannedExpirationDate) < 0:
                    jiraDaysUntilPlannedExpirationDate = "-1"

                if int(jiraDaysUntilPlannedExpirationDate) > 0:
                    if jiraStatus == "Closed":
                        jiraExemptionStatus = "Closed"

            # DR Exemption Data List
            dataTemplate = "{jira_exemption_status},{jira_key},{jira_status},{jira_resolution},{jira_design_rule_tag},{jira_helm_chart_name},{jira_planned_expiration_date},{jira_days_until_planned_expiration_date},{jira_email_distribution_list},{jira_reporter_name},{jira_reporter_email},{jira_assignee_name},{jira_assignee_email},{jira_type}\n"
            dataString = dataTemplate.format(
                jira_exemption_status=jiraExemptionStatus,
                jira_key=jiraKey,
                jira_status=jiraStatus,
                jira_resolution=jiraResolution,
                jira_design_rule_tag=jiraDesignRuleTag,
                jira_helm_chart_name=jiraHelmChartName,
                jira_planned_expiration_date=jiraPlannedExpirationDate,
                jira_days_until_planned_expiration_date=jiraDaysUntilPlannedExpirationDate,
                jira_email_distribution_list=jiraEmailDistributionList,
                jira_reporter_name=jiraReporterName,
                jira_reporter_email=jiraReporterEmail,
                jira_assignee_name=jiraAssigneeName,
                jira_assignee_email=jiraAssigneeEmail,
                jira_type=jiraType
            )

            designRuleExemptionData.append(dataString.split(","))

            # Data Arrangement
            # 0 -> Exemption Status
            # 1 -> JIRA Key
            # 2 -> JIRA Status
            # 3 -> JIRA Resolution
            # 4 -> Exempt DR Tag
            # 5 -> Helm Chart Name
            # 6 -> Planned Expiration Date
            # 7 -> Days Until Planned Expiration Date
            # 8 -> Email Distribution List
            # 9 -> Reporter Name
            # 10 -> Reporter Email
            # 11 -> Assignee Name
            # 12 -> Assignee Email
            # 13 -> JIRA Type


# Report Generation
def generateReport():

    global report
    global reportHeader
    global designRuleExemptionData

    # DR_Exemption_Requests.csv
    # Header
    with open(report, "a") as outputFile:
        outputFile.write(reportHeader)
    outputFile.close()

    # Data
    if designRuleExemptionData:
        for data in designRuleExemptionData:
            reportData = ",".join(data)
            with open(report, "a") as outputFile:
                outputFile.write(reportData)
            outputFile.close()


# Categorize DR Exemption Requests
def categorizeDesignRuleExemptions():

    global designRuleExemptionData
    global designRuleExemptionData_Expired
    global designRuleExemptionData_SoonToBe_Expired

    # Categorize Requests based on the Exemption Status
    if designRuleExemptionData:
        for data in designRuleExemptionData:
            jiraExemptionStatus = str(data[0])
            jiraStatus = str(data[2])
            jiraDesignRuleTag = str(data[4])
            jiraHelmChartName = str(data[5])

            if(jiraStatus == "Approved" and "test-run" not in jiraDesignRuleTag and "Test_Skip_Request" not in jiraDesignRuleTag and "test-run" not in jiraHelmChartName):
                if jiraExemptionStatus == "Expired":
                    designRuleExemptionData_Expired.append(data) # Remove DR Exemption config from helm-dr-properties.yaml
                elif jiraExemptionStatus == "Soon to be Expired":
                    designRuleExemptionData_SoonToBe_Expired.append(data) # Send Email Notification


# Email Notification
def sendEmailNotification():

    global designRuleExemptionData_Expired
    global designRuleExemptionData_SoonToBe_Expired
    senderEmail = "jenkins-ossadmin-no-reply@ericsson.com"

    # Email notification on Expiration
    if designRuleExemptionData_SoonToBe_Expired:
        for data in designRuleExemptionData_SoonToBe_Expired:
            jiraKey = str(data[1])
            jiraPlannedExpirationDate = str(data[6])
            jiraDaysUntilPlannedExpirationDate = str(data[7])
            jiraEmailDistributionList = str(data[8]).replace(";",",")
            jiraReporterName = str(data[9])
            jiraReporterEmail = str(data[10]).rstrip()
            jiraAssigneeName = str(data[11])
            jiraAssigneeEmail = str(data[12]).rstrip()
            jiraLinkTemplate = "https://jira-oss.seli.wh.rnd.internal.ericsson.com/browse/{jira_key}"
            jiraLink = jiraLinkTemplate.format(jira_key=jiraKey)

            # Email Subject
            emailSubjectTemplate = "Action Required! [{jira_key}] DR Exemption Request expires in {jira_days_until_planned_expiration_date} days!"
            emailSubject = emailSubjectTemplate.format(
                jira_key=jiraKey,
                jira_days_until_planned_expiration_date=jiraDaysUntilPlannedExpirationDate,
            )

            # Email Body
            emailBodyTemplate = (
                "Hello {jira_reporter_name},<br><br>"
                + "We wanted to inform you that your design rule exemption request {jira_link} expires in {jira_days_until_planned_expiration_date} days.<br><br>"
                + "If you're using the hybrid version of microservice CI pipelines on <a href='https://fem1s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/'>fem1s11-eiffel216</a> or <a href='https://fem6s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/'>fem6s11-eiffel216</a>, TheHummingbirds' automation will remove your exemption on <b>{jira_planned_expiration_date}</b>.<br><br>"
                + "If you happen to be using a pipeline version that isn't hybrid, or if the exemption isn't at the CI level, please take appropriate action before the 'Planned Expiration Date' and remove the exemption from your end.<br><br>"
                + "Kindly note that you will keep receiving emails until you confirm to ODP that you have lifted the exemption and ODP changes the ticket to 'Closed' status. We appreciate your timely attention to this matter.<br><br>"
                + "Should you have any queries, please feel free to contact ODP without delay.<br><br>"
                + "cc: @{jira_assignee_name} (Assignee of the DR Exemption Request JIRA)<br><br>"
                + "Regards, <br>The Hummingbirds (On behalf of ODP)"
            )

            emailBody = emailBodyTemplate.format(
                jira_reporter_name=jiraReporterName,
                jira_link=jiraLink,
                jira_days_until_planned_expiration_date=jiraDaysUntilPlannedExpirationDate,
                jira_planned_expiration_date=jiraPlannedExpirationDate,
                jira_assignee_name=jiraAssigneeName,
            )

            # Email Command
            commandTemplate = """
            (
            echo To:"{jira_reporter_email}"
            echo CC:"PDLODPDREX@pdl.internal.ericsson.com, {jira_assignee_email}, {jira_email_distribution_list}"
            echo From: "{sender_email}"
            echo "Content-Type: text/html;"
            echo Subject: "{email_subject}"
            echo "{email_body}"
            ) | sendmail -t"""

            command = commandTemplate.format(
                jira_reporter_email=jiraReporterEmail,
                jira_assignee_email=jiraAssigneeEmail,
                jira_email_distribution_list=jiraEmailDistributionList,
                sender_email=senderEmail,
                email_subject=emailSubject,
                email_body=emailBody,
            )

            executeShell(command)


    # Email notification to remove expired exemption
    if designRuleExemptionData_Expired:
        for data in designRuleExemptionData_Expired:
            jiraKey = str(data[1])
            jiraPlannedExpirationDate = str(data[6])
            jiraDaysUntilPlannedExpirationDate = str(data[7])
            jiraEmailDistributionList = str(data[8]).replace(";",",")
            jiraReporterName = str(data[9])
            jiraReporterEmail = str(data[10]).rstrip()
            jiraAssigneeName = str(data[11])
            jiraAssigneeEmail = str(data[12]).rstrip()
            jiraLinkTemplate = "https://jira-oss.seli.wh.rnd.internal.ericsson.com/browse/{jira_key}"
            jiraLink = jiraLinkTemplate.format(jira_key=jiraKey)

            # Email Subject
            emailSubjectTemplate = "Action Required! [{jira_key}] DR Exemption Request has expired!"
            emailSubject = emailSubjectTemplate.format(
                jira_key=jiraKey
            )

            # Email Body
            emailBodyTemplate = (
                "Hello {jira_reporter_name},<br><br>"
                + "We wanted to inform you that your design rule exemption request {jira_link} has expired.<br><br>"
                + "If you're using the hybrid version of microservice CI pipelines on <a href='https://fem1s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/'>fem1s11-eiffel216</a> or <a href='https://fem6s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/'>fem6s11-eiffel216</a>, TheHummingbirds' automation should have removed your exemption config already. Please verify if the automation removed your exemption config from the <a href='https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.ci/oss-common-ci-utils/+/refs/heads/dVersion-2.0.0-hybrid/dsl/helm-dr-properties.yaml'>helm-dr-properties.yaml</a> and inform ODP to move the exemption request ticket to 'Closed' status.<br><br>"
                + "If you happen to be using a pipeline version that isn't hybrid, or if the exemption isn't at the CI level, please remove the exemption from your end. After that, please let ODP know so they can close the exception request ticket.<br><br>"
                + "Kindly note that you will keep receiving emails until you confirm to ODP that you have lifted the exemption and ODP changes the ticket to 'Closed' status. We appreciate your timely attention to this matter.<br><br>"
                + "Should you have any queries, please feel free to contact ODP without delay.<br><br>"
                + "cc: @{jira_assignee_name} (Assignee of the DR Exemption Request JIRA)<br><br>"
                + "Regards, <br>The Hummingbirds (On behalf of ODP)"
            )

            emailBody = emailBodyTemplate.format(
                jira_reporter_name=jiraReporterName,
                jira_link=jiraLink,
                jira_assignee_name=jiraAssigneeName
            )

            # Email Command
            commandTemplate = """
            (
            echo To:"{jira_reporter_email}"
            echo CC:"PDLODPDREX@pdl.internal.ericsson.com, {jira_assignee_email}, {jira_email_distribution_list}"
            echo From: "{sender_email}"
            echo "Content-Type: text/html;"
            echo Subject: "{email_subject}"
            echo "{email_body}"
            ) | sendmail -t"""

            command = commandTemplate.format(
                jira_reporter_email=jiraReporterEmail,
                jira_assignee_email=jiraAssigneeEmail,
                jira_email_distribution_list=jiraEmailDistributionList,
                sender_email=senderEmail,
                email_subject=emailSubject,
                email_body=emailBody,
            )

            executeShell(command)


# Remove Expired DR Exemptions
def removeExpiredDesignRuleExemptions():

    global designRuleExemptionData_Expired
    regexPatternList=[]
    defaultValue = "<Please complete>"
    helmPropertiesFile = "oss-common-ci-utils/dsl/helm-dr-properties.yaml"
    helmPropertiesContent = ""
    senderEmail = "jenkins-ossadmin-no-reply@ericsson.com"

    if designRuleExemptionData_Expired:

        # Clone OSS/com.ericsson.oss.ci/oss-common-ci-utils (dVersion-2.0.0-hybrid)
        command = """
        [ -d oss-common-ci-utils ] && rm -rf oss-common-ci-utils
        git clone ${GERRIT_MIRROR}/OSS/com.ericsson.oss.ci/oss-common-ci-utils
        cd oss-common-ci-utils
        git checkout dVersion-2.0.0-hybrid
        """
        executeShell(command)

        # Read helm-dr-properties.yaml content
        with open(helmPropertiesFile, "r") as inputFile:
            helmPropertiesContent = inputFile.read().replace("\n", "")
        inputFile.close()

        # Remove Expired DR Exemptions from helm-dr-properties.yaml
        for data in designRuleExemptionData_Expired:
            jiraKey = str(data[1])
            jiraDesignRuleTag = str(data[4])
            jiraHelmChartName = str(data[5])
            jiraEmailDistributionList = str(data[8]).replace(";",",")
            jiraReporterName = str(data[9])
            jiraReporterEmail = str(data[10]).rstrip()
            jiraAssigneeName = str(data[11])
            jiraAssigneeEmail = str(data[12]).rstrip()
            jiraLinkTemplate = "https://jira-oss.seli.wh.rnd.internal.ericsson.com/browse/{jira_key}"
            jiraLink = jiraLinkTemplate.format(jira_key=jiraKey)

            # Regex Pattern
            if (jiraDesignRuleTag != defaultValue and jiraHelmChartName != defaultValue):

                # Program Level Exemptions
                if jiraHelmChartName == "program-level":
                    regexPatternTemplate = "-DhelmDesignRule.config.{jira_design_rule_tag}=exempt;{jira_key};{jira_link};{jira_reporter_rame};{jira_reporter_email};{jira_assignee_name};{jira_assignee_email};{jira_email_distribution_list}"
                    for designRuleTag in jiraDesignRuleTag.split(";"):
                        regexPattern = regexPatternTemplate.format(
                            jira_design_rule_tag=designRuleTag,
                            jira_key=jiraKey,
                            jira_link=jiraLink,
                            jira_reporter_rame=jiraReporterName,
                            jira_reporter_email=jiraReporterEmail,
                            jira_assignee_name=jiraAssigneeName,
                            jira_assignee_email=jiraAssigneeEmail,
                            jira_email_distribution_list=jiraEmailDistributionList,
                        )
                        regexPatternList.append(regexPattern)

                # Microservice Level Exemptions
                else:
                    regexPatternTemplate = "-DhelmDesignRule.config.{jira_helm_chart_name}.{jira_design_rule_tag}=exempt;{jira_key};{jira_link};{jira_reporter_rame};{jira_reporter_email};{jira_assignee_name};{jira_assignee_email};{jira_email_distribution_list}"
                    for designRuleTag in jiraDesignRuleTag.split(";"):
                        for helmChartName in jiraHelmChartName.split(";"):
                            regexPattern = regexPatternTemplate.format(
                                jira_helm_chart_name=helmChartName,
                                jira_design_rule_tag=designRuleTag,
                                jira_key=jiraKey,
                                jira_link=jiraLink,
                                jira_reporter_rame=jiraReporterName,
                                jira_reporter_email=jiraReporterEmail,
                                jira_assignee_name=jiraAssigneeName,
                                jira_assignee_email=jiraAssigneeEmail,
                                jira_email_distribution_list=jiraEmailDistributionList,
                            )
                            regexPatternList.append(regexPattern)

        # Regex Validation
        for data in regexPatternList:
            print("\n" + data)
            regexPattern = data.split(";")[0]
            jiraKey = data.split(";")[1]
            jiraLink = data.split(";")[2]
            jiraReporterName = data.split(";")[3]
            jiraReporterEmail = data.split(";")[4]
            jiraAssigneeName = data.split(";")[5]
            jiraAssigneeEmail = data.split(";")[6]
            jiraEmailDistributionList = data.split(";")[7]

            if re.search(regexPattern, helmPropertiesContent):
                errorMessageTemplate = "[{jira_key}] The config '{regex_pattern}' is found in the helm-dr-properties.yaml"
                errorMessage = errorMessageTemplate.format(
                    jira_key=jiraKey,
                    regex_pattern=regexPattern,
                )
                print(errorMessage)

                # Remove the Regex Pattern from helm-dr-properties.yaml
                with open(helmPropertiesFile, "r") as inputFile:
                    newlines = []
                    for line in inputFile.readlines():
                        newlines.append(line.replace(regexPattern, ""))
                inputFile.close()

                with open(helmPropertiesFile, "w") as outputFile:
                    for line in newlines:
                        outputFile.write(line)
                outputFile.close()

                # Merge the changes to OSS/com.ericsson.oss.ci/oss-common-ci-utils (dVersion-2.0.0-hybrid)
                commandTemplate = """
                cd oss-common-ci-utils
                git status
                git add dsl/helm-dr-properties.yaml
                git commit -m "[{jira_key}] Removed Expired DR Exemption"
                git remote set-url --push origin ssh://gerrit-gamma.gic.ericsson.se:29418/OSS/com.ericsson.oss.ci/oss-common-ci-utils
                git push origin HEAD:dVersion-2.0.0-hybrid
                """
                command = commandTemplate.format(jira_key=jiraKey)
                executeShell(command)

                errorMessageTemplate = "[{jira_key}] The config '{regex_pattern}' is removed from the helm-dr-properties.yaml"
                errorMessage = errorMessageTemplate.format(
                    jira_key=jiraKey,
                    regex_pattern=regexPattern,
                )
                print(errorMessage)

                # Send Email confirmation
                # Email Subject
                emailSubjectTemplate = "Action Required! [{jira_key}] DR Exemption config has been removed!"
                emailSubject = emailSubjectTemplate.format(
                    jira_key=jiraKey
                )

                # Email Body
                emailBodyTemplate = (
                    "Hello {jira_reporter_name},<br><br>"
                    + "We wanted to inform you that your design rule exemption request {jira_link} has expired.<br><br>"
                    + "Since you're using the hybrid version of microservice CI pipelines on <a href='https://fem1s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/'>fem1s11-eiffel216</a> or <a href='https://fem6s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/'>fem6s11-eiffel216</a>, TheHummingbirds' automation has removed your exemption config. Please verify if the automation removed your exemption config from the <a href='https://gerrit-gamma.gic.ericsson.se/plugins/gitiles/OSS/com.ericsson.oss.ci/oss-common-ci-utils/+/refs/heads/dVersion-2.0.0-hybrid/dsl/helm-dr-properties.yaml'>helm-dr-properties.yaml</a> and inform ODP to move the exemption request ticket to 'Closed' status.<br><br>"
                    + "Kindly note that you will keep receiving emails until you confirm to ODP that the automation has lifted the exemption and ODP changes the ticket to 'Closed' status. We appreciate your timely attention to this matter.<br><br>"
                    + "Should you have any queries, please feel free to contact ODP without delay.<br><br>"
                    + "cc: @{jira_assignee_name} (Assignee of the DR Exemption Request JIRA)<br><br>"
                    + "Regards, <br>The Hummingbirds (On behalf of ODP)"
                )

                emailBody = emailBodyTemplate.format(
                    jira_reporter_name=jiraReporterName,
                    jira_link=jiraLink,
                    jira_assignee_name=jiraAssigneeName
                )

                # Email Command
                commandTemplate = """
                (
                echo To:"{jira_reporter_email}"
                echo CC:"PDLODPDREX@pdl.internal.ericsson.com, PDLAEONICC@pdl.internal.ericsson.com, {jira_assignee_email}, {jira_email_distribution_list}"
                echo From: "{sender_email}"
                echo "Content-Type: text/html;"
                echo Subject: "{email_subject}"
                echo "{email_body}"
                ) | sendmail -t"""

                command = commandTemplate.format(
                    jira_reporter_email=jiraReporterEmail,
                    jira_assignee_email=jiraAssigneeEmail,
                    jira_email_distribution_list=jiraEmailDistributionList,
                    sender_email=senderEmail,
                    email_subject=emailSubject,
                    email_body=emailBody,
                )

                executeShell(command)

            else:
                errorMessageTemplate = "[{jira_key}] The config '{regex_pattern}' is not found in the helm-dr-properties.yaml"
                errorMessage = errorMessageTemplate.format(
                    jira_key=jiraKey,
                    regex_pattern=regexPattern,
                )
                print(errorMessage)


# Main Function
def main():
    if len(sys.argv) != 2:
        sys.exit("Error: Function name is not supplied!")

    functionName = sys.argv[1]
    if functionName == "validateDesignRuleExemptions":
        validateDesignRuleExemptions()


if __name__ == "__main__":
    main()
