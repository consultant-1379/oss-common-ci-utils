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
import sys
from requests import get
from email_sender import create_email

# Variables
username = os.environ.get("GERRIT_USERNAME")
password = os.environ.get("GERRIT_PASSWORD")
request_timeout = os.environ.get("REQUEST_TIMEOUT")


def access_check(instance, url):
    try:
        print("Checking connectivity to " + url + " Timeout for the connection is " + request_timeout + " seconds.")
        get(url, auth=(username, password), timeout=int(request_timeout))
        print("Connection to " + instance + " successful")
    except Exception:
        create_email(instance)
        print("Connection to " + instance + " unsuccessful. Reason:")
        raise


# Main Function
def main():
    if len(sys.argv) < 2:
        raise ValueError("Error: Invalid arguments! Please provide the tool name and URL.")

    instance = sys.argv[1]
    url = sys.argv[2]

    access_check(instance, url)


if __name__ == "__main__":
    main()
