#!/usr/bin/env python3
#
# COPYRIGHT Ericsson 2024
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
import os.path
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Jenkins's environment variables
JOB_NAME = os.environ.get("JOB_NAME")
BUILD_URL = os.environ.get("BUILD_URL")
EMAIL = os.environ.get("EMAIL")

# local variables
email_template = "ci/configs/healthcheck/email_template.html"

# SMTP configurations
smtp_server_url = "smtp-seli.lx.gic.ericsson.se"  # SMTP server linked to the Jenkins FEM
smtp_port = 25

# email configuration
jenkins_oss_admin_email = "jenkins-ossadmin-no-reply@ericsson.com"


# Create email notification.
def create_email(instance_name):
    html_message = read_from_file() \
        .replace("instance_name", instance_name) \
        .replace("job_url", BUILD_URL) \
        .replace("job_name", JOB_NAME)

    email_content = MIMEMultipart("alternative")
    email_content["From"] = jenkins_oss_admin_email
    email_content["To"] = EMAIL
    email_content["Subject"] = "Health check: Issue detected in " + instance_name

    mime_email_message = MIMEText(html_message, "html")
    email_content.attach(mime_email_message)

    send_email(email_content.as_string())


def read_from_file():
    with open(email_template) as file:
        return file.read()


def send_email(email_content):
    global smtp_server
    try:
        smtp_server = smtplib.SMTP(smtp_server_url, smtp_port)
        smtp_server.sendmail(jenkins_oss_admin_email, EMAIL, email_content)
        print("Email sent successfully!")
    except smtplib.SMTPResponseException as ex:
        print("Something went wrong!", ex)
    finally:
        smtp_server.close()
