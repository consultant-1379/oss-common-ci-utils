import requests
import os
import pandas as pd

offline_token = os.environ.get("SCAS_REFRESH_TOKEN")

input_file = "FOSS_uploaded.xls"
output_file = "Updated_Stako.xls"
data = pd.read_excel(input_file)
count = 0

print("**********************************************")
print("Total Number of entries:", len(data))
print("Column Names:", data.columns.values.tolist())
print("**********************************************")

access_token_url = "https://scas.internal.ericsson.com/auth/realms/SCA/protocol/openid-connect/token"
payload = "grant_type=refresh_token&client_id=scas-ext-client-direct&refresh_token=" + offline_token
headers = {"Content-Type": "application/x-www-form-urlencoded"}
response = requests.request("POST", access_token_url, headers=headers, data=payload)
access_token = response.json()["access_token"]

for i in range(len(data)):
    print(f"Row: {i} '3PP Name': {data.loc[i, '3PP Name']}")
    name = data.loc[i, "3PP Name"]
    version = data.loc[i, "3PP Version"]
    print(f"Row: {i} '3PP Version': {data.loc[i, '3PP Version']}")
    new_version = str(version).replace("/", "\/")
    print("3pp version is:" + new_version)
    count += 1

    scas_component_url = "https://scas.internal.ericsson.com/ordering/components/search?filter=compName,likei,*{_name_3PP}*&filter=compVersion,likei,*{_new_version_3PP}*&access_token={_access_token}"
    scas_component_url = scas_component_url.format(
        _access_token=access_token, _name_3PP=name, _new_version_3PP=new_version
    )
    payload = ""
    headers = {}
    response = requests.request("GET", scas_component_url, headers=headers, data=payload)
    json_value = response.json()

    if json_value:
        for value in json_value["content"]:
            stako_code = str(value["stakoCode"])
            restriction_code = str(value["restrictionCode"])
        print(f"Returned 'stako': {stako_code}")
        data.loc[i, "Stako"] = stako_code
        data.loc[i, "RE Code"] = restriction_code
        print(f"Returned 'RE': {restriction_code}")
    print("-----------------------------------------")

print("Number of FOSS: ", count)
print("-----------------------------------------")
data.to_excel(output_file, index=False)
print("-----------------------------------------")