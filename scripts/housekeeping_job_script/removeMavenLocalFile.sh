#! /bin/bash

# This script will help to remove the currupted maven file locally

echo 'Removing the file' "$1"

#cd /home/ossadmin/.m2/repository/ || exit
cd /proj/mvn/.m2/repository/ || exit

if [ -f "$1" ]
then
  echo 'File is present'
  echo 'Removing the file' "$1"
  rm -rf "$1"
else
  echo 'no such file found'
  exit 1
fi
