#!/usr/bin/python3
import os

os.system("qrsh -q ossmsci.q -l hostname=seliius26249.seli.gic.ericsson.se")
os.chdir("/home/ossadmin/")
with open("munin_token") as f:
    existing_token = f.read()

print("Refresh Token: " + existing_token)
