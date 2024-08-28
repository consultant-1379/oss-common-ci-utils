#! /bin/bash

femServer=$1
JCaaC=$2
configFile=$3

JENKINS_JAR=jenkins_config_as_code/scripts/jenkins-cli.jar
PASSWORD=$(cat secret)
FEMSERVER=https://${femServer}-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/
config=jenkins_config_as_code/configFiles/${configFile}


if [ "$JCaaC" = "true" ]
then
    if [ -f "$config" ]
    then
        echo ' ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ' "$config" ' ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
        cat /proj/eiffel216_config_"$femServer"/eiffel_home/"${femServer}"_JCasC.yaml
        echo '---------------'to copy "$configFile" 'File into Jenkins HOME directory for configuration---------------'
        #scp "$config" /proj/eiffel216_config_"$femServer"/eiffel_home/"${femServer}"_configFile.yaml
        scp "$config" /proj/eiffel216_config_"$femServer"/eiffel_home/"${femServer}"_JCasC.yaml
        echo ' ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'

        cat /proj/eiffel216_config_"$femServer"/eiffel_home/"${femServer}"_configFile.yam
        echo ' ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
   
        echo ''
        cat /proj/eiffel216_config_"$femServer"/eiffel_home/"${femServer}"_JCasC.yaml
        echo ' ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
        
        echo ''
        echo ''
        echo '---------------to reload jcasc configuration on' "$femServer" 'server---------------'
        echo ''
        echo ''
        java -jar $JENKINS_JAR -auth "${USER}":"${PASSWORD}" -s "$FEMSERVER" reload-jcasc-configuration
        echo ''
        echo ''
        echo '---------------Jenkins Configuration as code implementation finished on' "$femServer" 'server---------------'
    else
        echo '-----------------------'"${femServer}"' Config YAML file Not Found----------------------------'
        exit 1
    fi
else
    echo '############################# Jenkins Configuration as a Code skipped for '"$femServer"' #############################'
fi
