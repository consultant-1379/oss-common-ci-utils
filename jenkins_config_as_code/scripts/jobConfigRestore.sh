#! /bin/bash

backupPath=/proj/ossmsci/jenkinsBackup
backupPathList=$(ls /proj/ossmsci/jenkinsBackup)
rm -rf ${backupPath}/backupFile
echo '####---- Job config file backup found for below Jenkins FEM  ----####'
echo ''
echo ''
x=1
for backupFiles in ${backupPathList}
do
  echo ${x} ')' "${backupFiles}"|cut -d "_" -f1
  echo "${backupFiles}"|cut -d "." -f1
  echo ''
  ((x+=1))
  echo "${backupFiles}" >> backupFile
done

echo ' Select FEM to restore job config files '
read -r femServer

mv backupFile ${backupPath}
cd ${backupPath} || { echo "Backup path does not exist"; exit 1; }

if [ "$femServer" == "1" ]
then
    backupfile=$(< backupFile awk 'NR==1')
    fem=$(< backupFile awk 'NR==1'|cut -d "_" -f1)
    tar -xzf "$backupfile"
    cd jobConfigFile"${fem}" || { echo "Job Config File directory does not exist"; exit 1; }
    echo '############## Restore started ###############'
    echo ''
    scp -r ./* /proj/eiffel216_config_"${fem}"/eiffel_home/jobs/
    echo ''
    echo '############## Restore Finished for '"${fem}"'###############'
    cd ../
    rm -rf jobConfigFile"${fem}"
    rm -rf backupFile

elif [ "$femServer" == "2" ]
then
    backupfile=$(< backupFile awk 'NR==2')
    fem=$(< backupFile awk 'NR==2'|cut -d "_" -f1)
    tar -xzf "$backupfile"
    cd jobConfigFile"${fem}" || { echo "Job Config File directory does not exist"; exit 1; }
    echo '############## Restore started ###############'
    echo ''
    scp -r ./* /proj/eiffel216_config_"${fem}"/eiffel_home/jobs/
    echo ''
    echo '############## Restore Finished for '"${fem}"'###############'
    cd ../
    rm -rf jobConfigFile"${fem}"
    rm -rf backupFile

elif [ "$femServer" == "3" ]
then
    backupfile=$(< backupFile awk 'NR==3')
    fem=$(< backupFile awk 'NR==3'|cut -d "_" -f1)
    tar -xzf "$backupfile"
    cd jobConfigFile"${fem}" || { echo "Job Config File directory does not exist"; exit 1; }
    echo '############## Restore started ###############'
    echo ''
    scp -r ./* /proj/eiffel216_config_"${fem}"/eiffel_home/jobs/
    echo ''
    echo '############## Restore Finished for '"${fem}"'###############'
    cd ../
    rm -rf jobConfigFile"${fem}"
    rm -rf backupFile

else
   echo 'Please provide the correct input'
fi