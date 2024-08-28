#!/usr/bin/python3
#
# COPYRIGHT Ericsson 2022
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
import sys
import csv
import json
import os.path
import requests
from os.path import exists

# Variables
# HTTP Request
username = os.environ.get("GERRIT_USERNAME")
password = os.environ.get("GERRIT_PASSWORD")
url = 'https://eteamproject.internal.ericsson.com/rest/api/2/search?jql=PROJECT = "ADPPRG" AND issuetype = "DR Check" AND "Planned Enforcement Date" >= now() AND "Planned Enforcement Date" < 90d AND (status = PLANNED OR status = "Checked (Gracefully)" OR status = CHECKED OR status = "In Progress") ORDER BY "Planned Enforcement Date", "DR Tag", "Key"'

# Data and Report Generation
data = []
report = os.environ.get("REPORT")
reportHeader = ["JIRA Key", "DR Tag", "Status", "DR Checker Tool", "Planned Enforcement Date"]


# Functions
# Fetch ADP DR Enforcement Data
def fetchDesignRuleEnforcements():
    results = ""
    response = requests.get(url, auth=(username, password))
    if response.status_code == 200:
        results = response.json()
    else:
        errorMessageTemplate = "[Error]: HTTP Request to the ADP JIRA Board returned the status code - {status_code}!"
        errorMessage = errorMessageTemplate.format(status_code=str(response.status_code))
        sys.exit(errorMessage)

    if results:
        for value in results["issues"]:
            dict = {
                "JIRA Key": value["key"],
                "DR Tag": value["fields"]["customfield_31712"],
                "Status": value["fields"]["status"]["name"],
                "DR Checker Tool": str(value["fields"]["customfield_31714"]).replace(",", ";").replace("None", "-"),
                "Planned Enforcement Date": value["fields"]["customfield_31713"],
            }
            data.append(dict)

        # Generate Report
        if data:
            generateCSVReport(report, data)

# Generate CSV Report
def generateCSVReport(outputFile, data):
    if data:
        with open(outputFile, "w") as outputFile:
            writer = csv.DictWriter(outputFile, fieldnames=reportHeader)
            writer.writeheader()
            writer.writerows(data)

# Main Function
def main():
    if len(sys.argv) != 2:
        print("Error: Function name not supplied!")
        exit()

    functionName = sys.argv[1]
    if functionName == "fetchDesignRuleEnforcements":
        fetchDesignRuleEnforcements()


if __name__ == "__main__":
    main()