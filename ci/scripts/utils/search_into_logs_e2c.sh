#!/bin/bash
# Define vars
# JENKINS="all"
# TEXT="ERICenmdeploymenttemplates_CXP9031758/pom.xml"
# TYPE="all"
# list of Jenkins instance to be processed into an array
FEM="fem1s11 fem2s11 fem3s11 fem4s11 fem5s11 fem6s11 fem7s11 fem8s11"
IFS=' ' read -ra ADDR <<< "$FEM"
numJobs=0
function searchFem(){
    HOST=$1
    dirs=( $(find /proj/eiffel216_config_$HOST/eiffel_home/jobs/. -maxdepth 1 -type d -printf '%P\n') )
    for j in ${dirs[@]};
    do
        JOB_NAME_C=$(echo $j | awk '{print tolower($0)}')
        TYPE_C=$(echo $TYPE | awk '{print tolower($0)}')
        if  [[ $JOB_NAME_C == *"$TYPE_C"* ]] || [[ $TYPE == "all" ]]
        then
            BUILDS_PATH=/proj/eiffel216_config_$HOST/eiffel_home/jobs/$j/builds
            if [ -d "$BUILDS_PATH" ]
            then
                RES=$( grep -lr --include="log" "$TEXT*" $BUILDS_PATH)
                if [[ ! -z "$RES" ]]
                then
                    numJobs=$((numJobs+1))
                    echo Job $numJobs: https://$HOST-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/$j
                    printf '\n'
                fi
            fi
        fi
    done
}
printf '====================================================================================\n'
echo Searching "$TEXT" in logs regarding $JENKINS jenkins jobs
printf '====================================================================================\n\n'
if [ "$JENKINS" == "all" ]
    then
        for JENKNAME in "${ADDR[@]}"
        do
            echo Fem: "$JENKNAME"
            searchFem "$JENKNAME"
        done
else
        searchFem "$JENKINS"
fi
printf '============================================================\n'
echo Jenkins jobs found: $numJobs
printf '============================================================\n'