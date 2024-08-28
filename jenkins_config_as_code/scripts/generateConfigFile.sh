#! /bin/bash

# This script is being tested using shellcheck. The below comments disable certain tests.
# To find out more visit: https://github.com/koalaman/shellcheck
# shellcheck disable=SC2154

Fem_Instance_Path="eiffel216_config_"${Destination_Fem}   # previously FemHomePathName / FemHostname
Eiffel_Component_Name=${Destination_Fem}"-eiffel216.eiffel.gic.ericsson.se"   #previously FemFullFQDN / FemFQDN
FemDigit=$(echo "${Destination_Fem}" | cut -c4)   # to add Fem specific digit for the Namespace name

# upload the config file
git_upload(){
    git status
    git add -A
    git status
    git commit -m "${Destination_Fem} config file added on gerrit repo"
    git push origin master -f
}

# Provided variables will be added in the config file
cp jenkins_config_as_code/configFiles/Template_JCasC_File.yaml ../tmp_generatedConfig.yaml
sed -i "s/Eiffel_Component_Name/${Eiffel_Component_Name}/g;s/Fem_Instance_Path/${Fem_Instance_Path}/g;s/Fem_Name/${Destination_Fem}/g;s/FemDigit/${FemDigit}/g;" ../tmp_generatedConfig.yaml

if [ "$Type" == Admin ]
then
    FILE=jenkins_config_as_code/configFiles/"${Destination_Fem}"_Admin_JCasC.yaml
else
    FILE=jenkins_config_as_code/configFiles/"${Destination_Fem}"_JCasC.yaml
fi

ls -lrth jenkins_config_as_code/configFiles/
if [ ! -f "$FILE" ]  #does not exist
then
    sed -i '1,3d' ../tmp_generatedConfig.yaml  # remove the 3 line heading from the Template file
    cp ../tmp_generatedConfig.yaml "$FILE"
fi

git_upload

