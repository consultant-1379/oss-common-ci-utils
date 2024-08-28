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
import sys
import subprocess
from dateutil.parser import parse
from datetime import date, datetime


# Variables
# Jenkins
jenkins_job_name = os.environ["JOB_NAME"]
jenkins_build_url = os.environ["BUILD_URL"]

# Email
recipient_email = os.environ["EMAIL"]
sender_email = "jenkins-ossadmin-no-reply@ericsson.com"
infra_channel_email = "b32734be.ericsson.onmicrosoft.com@emea.teams.ms"


# Common functions
# Execute shell commands
def _execute_shell(command):
    subprocess.call(command, shell=True)

# Execute shell commands with output
def execute_shell(command):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdoutdata, stderrdata = proc.communicate()

    # Error
    if stderrdata:
        print(stderrdata)
        exit(1)

    # Output
    if stdoutdata:
        print(stdoutdata)
    return stdoutdata

# Date parser
def is_date(string, fuzzy=False): #fuzzy=False considers string tokens while parsing
    try:
        parse(string, fuzzy=fuzzy)
        return True
    except ValueError:
        return False


# Functions
# Validate docker certificate
def validate_docker_certificate():
    command = "twic cert ls"
    output = execute_shell(command).strip().split("\n")[1]

    for data in output.split(" "):
        if data and is_date(data):
            expiration_date = data
            days_until_expiration = int(((datetime.strptime(expiration_date, "%Y-%m-%d").date()) - date.today()).days)

            # Send email notification
            if days_until_expiration <= 7:

                # Email subject
                email_subject_template = "Action required! Docker TSA certificate expires in {remaining_days} days!"
                email_subject = email_subject_template.format(remaining_days=str(days_until_expiration))

                # Email body
                email_body_template = (
                    "Hello TheHummingbirds,<br><br>"
                    + "The docker TSA certificate will expire on <b>{expiration}</b>. "
                    + "It is critical to renew the certificate as soon as possible.<br>"
                    + "To do this, please follow the steps below.<br>"
                    + "<ol><li>Please login into one of the Grid Engines.</li>"
                    + "<li>Run the command '<b>twic cert renew TSA_jenkins_ cert</b>' to renew the certificate.</li>"
                    + "<li>Enter the functional user password when prompted.</li>"
                    + "<li>Run the command '<b>twic cert ls</b>' and verify if the expiration date is updated.</li></ol>"
                    + "For more info, please refer to <a href='https://eteamspace.internal.ericsson.com/x/2iRke'>Agent configuration > TSA config commands</a>.<br><br>"
                    + "<b>Note</b>: This mail has been sent automatically from <a href='{job_url}'>{job_name}</a>"
                )
                email_body = email_body_template.format(
                    expiration=expiration_date,
                    job_url=jenkins_build_url,
                    job_name=jenkins_job_name,
                )

                # Email command
                command_template = """
                    (
                    echo To:"{recipient}"
                    echo CC:"{infra_channel}"
                    echo From: "{sender}"
                    echo "Content-Type: text/html;"
                    echo Subject: "{subject}"
                    echo "{body}"
                    ) | sendmail -t"""

                command = command_template.format(
                    recipient=recipient_email,
                    infra_channel=infra_channel_email,
                    sender=sender_email,
                    subject=email_subject,
                    body=email_body,
                )

                # Execute email command
                _execute_shell(command)


# Main Function
def main():
    if len(sys.argv) != 2:
        sys.exit("Error: Function name is not supplied!")

    functionName = sys.argv[1]
    if functionName == "validate_docker_certificate":
        validate_docker_certificate()

if __name__ == "__main__":
    main()