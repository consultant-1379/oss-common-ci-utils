#!/usr/bin/python3
import os.path
import json
import requests
from requests import RequestException


# helper methods
def write_token(token_location, new_token):
    with open(token_location, "w") as outputFile:
        outputFile.write(new_token)  # Update the value of the refresh token in GE file munin_token
        outputFile.close()


def get_token(token_response, token_name):
    return token_response["results"][0]["data"][token_name]


# Reading Existing Token
os.system("qrsh -q ossmsci.q -l hostname=seliius26249.seli.gic.ericsson.se")
os.chdir("/home/ossadmin/")
with open("munin_token") as f:
    existing_refresh_token = f.read()
# API call to generate new token
URL = "https://mimer.internal.ericsson.com/authn/api/v2/refresh-token"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-On-Behalf-Of": "ossadmin",
}
data = {"token": existing_refresh_token}
response = requests.post(URL, headers=headers, data=json.dumps(data))
if response.status_code == 200:  # Check successful HTTP response
    tokenResponse = json.loads(response.text)
    newRefreshToken = get_token(tokenResponse, "refresh_token")
    newAccessToken = get_token(tokenResponse, "access_token")
    if len(newRefreshToken) > 0 and len(newAccessToken) > 0:  # Check for non-empty tokens
        print("New Refresh Token is: " + newRefreshToken)
        write_token("munin_token", newRefreshToken)
        print("New Access Token is: " + newAccessToken)
        write_token("munin_access_token", newAccessToken)
else:
    raise RequestException(
        "Something went wrong! GET Refresh Token Response status_code: {}, response_text: {}".format(response.status_code, response.text))
