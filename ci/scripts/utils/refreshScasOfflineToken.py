import requests
import os
import sys

'''
Purpose of script to use the Scas offline token to ensure it stays valid.
Offline token is a token that never expires however it needs to be used at least once within a 30 day period to stay valid.
Offline token is used to request a 15 minute access token for Scas. Script will create the access token using the offline token and run simple GET request to /userInfo endpoint to ensure validity.
'''

# Variables
offline_token = os.environ.get("SCAS_REFRESH_TOKEN")
scas_oidc_base_url = "https://scas.internal.ericsson.com/auth/realms/SCA/protocol/openid-connect"

# Verify token refresh by running GET request towards SCAS OIDC user info endpoint
def scas_access_check(scas_oidc_base_url, offline_token):
    access_token = create_access_token(scas_oidc_base_url, offline_token)
    user_info_url = scas_oidc_base_url + "/userinfo"
    headers = {"Authorization": "Bearer " + access_token}

    try:
        response = requests.get(user_info_url, headers=headers)
        response.raise_for_status()
        print(response.text)
    except requests.exceptions.RequestException as e:
        print("Error running GET request.", e)

# Create 15 minute access token using offline token
def create_access_token(scas_oidc_base_url, offline_token):
    access_token_url = scas_oidc_base_url + "/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": "scas-ext-client-direct",
        "refresh_token": offline_token,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(access_token_url, headers=headers, data=data)
        response.raise_for_status()
        access_token = response.json().get("access_token")
        return access_token
    except requests.exceptions.RequestException as e:
        print("Error creating access token.", e)

# Main Function
def main():
    if len(sys.argv) != 2:
        sys.exit("Error: Function name is not supplied!")

    functionName = sys.argv[1]
    if functionName == "refreshScasOfflineToken":
        scas_access_check(scas_oidc_base_url, offline_token)

if __name__ == "__main__":
    main()