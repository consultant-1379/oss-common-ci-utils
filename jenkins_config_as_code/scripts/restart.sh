#! /bin/bash

femServer=$1
Restart=$2

JENKINS_JAR=jenkins_config_as_code/scripts/jenkins-cli.jar
PASSWORD=$(cat secret)
FEMSERVER=https://${femServer}-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/

if [ "${Restart}" == "Yes" ]
then
    echo 'Restart of' "$femServer" 'server triggered'
    echo ''
    java -jar $JENKINS_JAR -auth "${USER}":"${PASSWORD}" -s "$FEMSERVER" restart
    echo ''
    echo 'Restart of' "$femServer" 'server completed'
else
    echo '############################# Restart skipped for '"$femServer"' #############################'
fi
