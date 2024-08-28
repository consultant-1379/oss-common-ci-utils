#!/usr/bin/env python3
""" Test cases for the modules installed in the python docker image
    Dockerfile: scripts/docker/python-image/python_image.dockerfile
    Requirements: scripts/docker/python-image/python_image_requirements.txt
"""
import os
import os.path
import sys
import subprocess
import time
import datetime
from datetime import date
from datetime import datetime
import re
import fnmatch
import xml
import xml.dom.minidom
import xml.etree.ElementTree as ET
import csv
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import numpy as np
import requests
from requests.auth import HTTPBasicAuth
from dateutil.parser import parse


def _sys():
    """module:
    import sys
    """
    sys.exit(0)


def _xml():
    """modules:
    import os
    import os.path
    import xml
    import xml.dom.minidom
    import xml.etree.ElementTree as ET
    """
    username = os.environ.get("GERRIT_USERNAME")
    password = os.environ.get("GERRIT_PASSWORD")
    job_url = os.environ.get("JOB_URL")

    job_xml_url = str(job_url) + "/config.xml"
    file = "build/job_config.xml"
    response = requests.get(
        job_xml_url, auth=HTTPBasicAuth(username, password), timeout=20
    )

    if response.status_code == 200:
        root = ET.fromstring(response.text)
        tree = ET.ElementTree(root)
        tree.write(file)

    if os.path.exists(file):
        if os.path.isfile(file):
            print(file + " exists!")
            doc = xml.dom.minidom.parse(file)
            print(doc.nodeName)
            print(doc.firstChild.tagName)


def _datetime():
    """modules:
    import datetime
    from datetime import date
    from datetime import datetime
    """
    print(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
    print(((datetime.strptime("2050-12-31", "%Y-%m-%d").date()) - (date.today())).days)
    print(parse("Today is January 1, 2047 at 8:21:00AM", fuzzy_with_tokens=True))


def _re():
    """module:
    import re
    """
    regex_pattern = "COPYRIGHT Ericsson"
    file = "scripts/docker/python-image/python_image_ruleset.yaml"
    file_content = ""
    with open(file, encoding="utf-8") as input_file:
        file_content = input_file.read().replace("\n", "")
    input_file.close()
    if re.search(regex_pattern, file_content):
        print("The file has the expected license header!")


def _fnmatch():
    """module:
    import fnmatch
    """
    for file in os.listdir("."):
        if fnmatch.fnmatch(file, "*.txt"):
            print(file)


def _time():
    """module:
    import time
    """
    print("Printed immediately.")
    time.sleep(2)
    print("Printed after 2 seconds.")


def _subprocess():
    """module:
    import subprocess
    """
    command = "ls"
    with subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    ) as proc:
        stdoutdata, stderrdata = proc.communicate()
        if stdoutdata:
            print(stdoutdata)
        if stderrdata:
            print(stderrdata)


def _pandas():
    """module:
    import pandas as pd
    """
    d = {"col1": [1, 2], "col2": [3, 4]}
    df = pd.DataFrame(data=d)
    print(df)


def _numpy():
    """module:
    import numpy as np
    """
    arr = np.array([1, 2, 3, 4, 5])
    print(arr)


def _requests():
    """modules:
    import requests
    import csv
    """
    data = []
    username = os.environ.get("GERRIT_USERNAME")
    password = os.environ.get("GERRIT_PASSWORD")
    url = '''https://eteamproject.internal.ericsson.com/rest/api/2/search?jql=
    PROJECT = "ADPPRG" AND issuetype = "DR Check"
     AND "Planned Enforcement Date" >= now()
     AND "Planned Enforcement Date" < 90d
     AND (status = PLANNED
         OR status = "Checked (Gracefully)"
         OR status = CHECKED
         OR status = "In Progress")
     ORDER BY "Planned Enforcement Date", "DR Tag", "Key"'''
    report_header = [
        "JIRA Key",
        "DR Tag",
        "Status",
        "DR Checker Tool",
        "Planned Enforcement Date",
    ]

    response = requests.get(url, auth=(username, password), timeout=20)
    if response.status_code == 200:
        results = response.json()

    if results:
        for value in results["issues"]:
            _dict = {
                "JIRA Key": value["key"],
                "DR Tag": value["fields"]["customfield_31712"],
                "Status": value["fields"]["status"]["name"],
                "DR Checker Tool": value["fields"]["customfield_31714"],
                "Planned Enforcement Date": value["fields"]["customfield_31713"],
            }
            data.append(_dict)

    if data:
        with open("build/test.txt", "w", encoding="utf-8") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=report_header)
            writer.writeheader()
            writer.writerows(data)


def _json():
    """module:
    import json
    """
    sample_json = '{ "name":"John", "age":30, "city":"New York"}'
    sample_json = json.loads(sample_json)
    print(sample_json["age"])


def _email():
    """module:
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    """
    # SMTP configurations
    smtp_server_url = "smtp-seli.lx.gic.ericsson.se"  # SMTP server linked to the Jenkins FEM
    smtp_port = "25"

    # Email configurations
    email_from = "jenkins-ossadmin-no-reply@ericsson.com"
    email_to = "b32734be.ericsson.onmicrosoft.com@emea.teams.ms"  # Infra monitoring channel
    email_subject = "Test email"
    job_url = os.environ.get("JOB_URL")
    email_content = MIMEMultipart('alternative')
    email_content["From"] = email_from
    email_content["To"] = email_to
    email_content["Subject"] = email_subject

    # MIME type: text/html
    html_message = """\
            <div style="text-align:center;background:#2F4F4F;color:black;padding:10px;">
                <b>Neither the hummingbird nor the flower wonders how beautiful it is!</b>
            </div>
            <p>This is an automated email from: <a href='job_url'>job_url</a></p>
            """.replace("job_url", job_url)
    html_message = MIMEText(html_message, "html")
    email_content.attach(html_message)
    email_text = email_content.as_string()

    try:
        smtp_server = smtplib.SMTP(smtp_server_url, smtp_port)
        smtp_server.sendmail(email_from, email_to, email_text)
        smtp_server.close()
        print("Email sent successfully!")
    except smtplib.SMTPResponseException as ex:
        print("Something went wrong!", ex)


def main():
    """Main function"""
    _datetime()
    _re()
    _time()
    _subprocess()
    _pandas()
    _numpy()
    _requests()
    _json()
    _fnmatch()
    _xml()
    _email()
    _sys()


if __name__ == "__main__":
    main()
