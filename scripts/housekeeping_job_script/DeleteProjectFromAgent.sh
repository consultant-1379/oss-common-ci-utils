#!/bin/bash

# Script to delete the project folder on all of the agents per fem.

list=("RHEL7_GE_Docker_1" "RHEL7_GE_Docker_2" "RHEL7_GE_Docker_3" "RHEL7_GE_Docker_4" "RHEL7_GE_Docker_5" "RHEL7_GE_Docker_6")

command="/proj/eiffel216_config_FEM/agents/AGENT/workspace/"
command=${command/FEM/$fem}

echo "Parameters provided:"
echo "job name = ${NAME_OF_THE_JOB}"

for agent in "${list[@]}"; do  # loop through the array
    echo -e "\nagent = $agent"
    tmp_command=${command/AGENT/$agent}  # replace agents
  
    if [ -d $tmp_command ]
    then
        cd $tmp_command || exit
        cat "${NAME_OF_THE_JOB}"*

        if [ -d "${NAME_OF_THE_JOB}" ]
            then
                echo ">>>>> DELETING the ${NAME_OF_THE_JOB} folder"
                rm -rf "${NAME_OF_THE_JOB}"
                rm -rf "${NAME_OF_THE_JOB}"@tmp
                cat "${NAME_OF_THE_JOB}"*
        fi
    fi
done