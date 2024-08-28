#! /bin/bash

femServer=$1
configFile=$2


JENKINS_JAR=jenkins_config_as_code/scripts/jenkins-cli.jar
PASSWORD=$(cat secret)
FEMSERVER=https://${femServer}-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/
config=jenkins_config_as_code/configFiles/${configFile}


if [ "$configFile" ]
then
    if [ -f "$config" ]
    then
        echo ' ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
        cat /proj/eiffel216_config_"$femServer"/eiffel_home/"${femServer}"_JCasC.yaml
        echo ' ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'        
        #scp "$config" /proj/eiffel216_config_"$femServer"/eiffel_home/"${femServer}"_configFile.yaml
        scp "$config" /proj/eiffel216_config_"$femServer"/eiffel_home/"${femServer}"_JCasC.yaml
        
        echo -e '\n ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
        cat /proj/eiffel216_config_"$femServer"/eiffel_home/"${femServer}"_JCasC.yaml
        echo -e '\n ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'                                                                                 
        echo '---------------to reload jcasc configuration from Jenkins HOME directory for configuration---------------'
        java -jar $JENKINS_JAR -auth "${USER}":"${PASSWORD}" -s "$FEMSERVER" reload-jcasc-configuration
        echo -e '\n---------------Jenkins Configuration as a code implementation finished on' "$femServer" 'server---------------\n'
    else
        echo '-----------------------'"${femServer}"' Config YAML file Not Found----------------------------'
        exit 1
    fi
fi
