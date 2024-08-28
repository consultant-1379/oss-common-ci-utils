#! /bin/bash

# This script is being tested using shellcheck. The below comments disable certain tests.
# To find out more visit: https://github.com/koalaman/shellcheck
# shellcheck disable=SC2013

backupPath=/proj/ossmsci/jenkinsBackup
< /home/ossadmin/IDUN_repo/jenkins.xml grep -i fem|cut -d "<" -f2 |cut -d ">" -f1 > jenkinsFemList

#storing previous backup in case of failure of backup.

mkdir -p ${backupPath}/old_backup; mv ${backupPath}/*jobConfigFile* ${backupPath}/old_backup

for fem in $(cat jenkinsFemList)
    do
        jobConfigFilePath=/proj/eiffel216_config_${fem}/eiffel_home/jobs
        ls "${jobConfigFilePath}" > tmp
        mkdir -p $backupPath/jobConfigFile"${fem}"
        for i in $(cat tmp)
            do mkdir -p $backupPath/jobConfigFile"${fem}"/"$i"
            scp "${jobConfigFilePath}"/"$i"/config.xml ${backupPath}/jobConfigFile"${fem}"/"$i"
            echo $? >> ${backupPath}/exitCode
        done
    cd ${backupPath} || { echo "Backup path does not exist"; exit 1; }
    tar -czf "${fem}"_jobConfigFile_"$(date +%Y-%m-%d_%H-%M-%S)".tar.gz jobConfigFile"${fem}"
    echo $? >> ${backupPath}/exitCode
    rm -rf jobConfigFile"${fem}"
done
rm -rf tmp
rm -rf jenkinsFemList

for statusCode in $(cat exitCode)
    do
    if [ "${statusCode}" == "0" ]
    then
        cd ${backupPath} || { echo "Backup path does not exist"; exit 1; }
        rm -rf ${backupPath}/old_backup
        rm -rf ${backupPath}/exitCode
    else
        echo 'Backup of JenkinsJob not completed successfully'
        echo 'No new fresh backup taken place'
        echo 'restoring previous backup'
        break
    fi
done

# Restore of previous store backup in case of backup failure
restore () {
    rm -rf ${backupPath}/exitCode
    cd ${backupPath} || { echo "Backup path does not exist"; exit 1; }
    rm -rf ./*jobConfigFile*
    mv old_backup/* .
    rm -rf old_backup
}

oldBackup=${backupPath}/old_backup

if [ -d "${oldBackup}" ]
    then
       restore
fi
