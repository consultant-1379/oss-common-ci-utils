#! /bin/bash

# This script is being tested using shellcheck. The below comments disable certain tests.
# To find out more visit: https://github.com/koalaman/shellcheck
# shellcheck disable=SC2013

femServer=$1
pluginList=$2


JENKINS_JAR=jenkins_config_as_code/scripts/jenkins-cli.jar
PASSWORD=$(cat secret)
FEMSERVER=https://${femServer}-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/
plugin=jenkins_config_as_code/plugins/$pluginList


if [ "$pluginList" ]
then

    echo '----------------------------'"$femServer"'-eiffel216.eiffel.gic.ericsson.se ----------------------------------'
    echo ''
    echo ''

    echo '---------------------------------------Plugins before install-----------------------------------------------'
    echo ''
    echo ''

    java -jar $JENKINS_JAR -auth "${USER}":"${PASSWORD}" -s "$FEMSERVER" list-plugins
    echo ''
    echo ''
    echo '-----------------------------------------------Count---------------------------------------------------------'
    echo ''
    echo ''

    java -jar $JENKINS_JAR -auth "${USER}":"${PASSWORD}" -s "$FEMSERVER" list-plugins|wc -l
    echo ''
    echo ''
    echo '-------------------------------------------------------------------------------------------------------------'
    echo ''
    echo ''
    echo '---------------------------------------plugin install started------------------------------------------------'

    if [ -f "$plugin" ]
    then
        < "$plugin" cut -d "(" -f 2|cut -d ")" -f 1 > _plugin_
        for i in $(cat _plugin_); do java -jar $JENKINS_JAR -auth "${USER}":"${PASSWORD}" -s "$FEMSERVER" install-plugin "$i" -deploy ; done
    else
        echo '------------------------------------'"${femServer}"' Plugin file NOT Found-----------------------------------------------'
        exit 1
    fi

    echo '---------------------------------------Plugins After install-----------------------------------------------'
    echo ''
    echo ''

    java -jar $JENKINS_JAR -auth "${USER}":"${PASSWORD}" -s "$FEMSERVER" list-plugins

    echo ''
    echo ''
    echo '-----------------------------------------------Count---------------------------------------------------------'
    echo ''
    echo ''

    java -jar $JENKINS_JAR -auth "${USER}":"${PASSWORD}" -s "$FEMSERVER" list-plugins|wc -l

    echo ''
    echo ''
    echo '-------------------------------------------------------------------------------------------------------------'
    echo ''
    echo ''
else
    echo '################################# Plugin install skipped for '"$femServer"' #################################'
fi