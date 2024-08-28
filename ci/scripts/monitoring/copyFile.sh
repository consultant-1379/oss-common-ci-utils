#! /bin/bash

# This script is being tested using shellcheck. The below comments disable certain tests.
# To find out more visit: https://github.com/koalaman/shellcheck
# shellcheck disable=SC2154

yesterday=test-$( date -d "${dtd} -1 days" +'%Y-%m-%d' ).txt
scp /home/ossadmin/IDUN_repo/FUldap/"${yesterday}" .
