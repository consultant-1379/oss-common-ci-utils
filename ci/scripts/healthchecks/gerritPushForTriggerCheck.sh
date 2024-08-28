#!/bin/bash
git --version

echo "FILES CURRENTLY IN FILE SYSTEM"
ls -la

echo "CLONING REPO"
git clone ssh://ossadmin@gerrit-gamma-read.seli.gic.ericsson.se:29418/OSS/com.ericsson.oss.ci.test/eric-oss-gerrit-trigger-test && scp -p -P 29418 ossadmin@gerrit-gamma-read.seli.gic.ericsson.se:hooks/commit-msg eric-oss-gerrit-trigger-test/.git/hooks/

echo "FILES CLONED"
ls -la

echo "MOVING TO REPO FOLDER"
cd eric-oss-gerrit-trigger-test

find . -name "README.md" -exec sed -i "$ a Gerrit Trigger Check" {} \;
echo $?

echo "CHECKING BRANCH"
git branch

echo "ADDING > COMMITING > PUSHING"
git clean -fdx
git add .
git commit -m "No Jira - Gerrit Trigger Check Admin Job"
git remote set-url origin --push ${GERRIT_CENTRAL}/OSS/com.ericsson.oss.ci.test/eric-oss-gerrit-trigger-test
git push origin HEAD:refs/for/master &> git_push.txt
echo "git operations done here"
cat git_push.txt

#wait for PreCodeReviews to start in each fem
echo "///////////////////////////////"
sleep 5m

# Abandon patch
# Check for open changes on this project in Gerrit

#clean files
file_name="open-changes.txt"
echo "//////////// Open File //////////////"

if [ -f $file_name ]
then
    rm -rf $file_name
    touch $file_name
else
    touch $file_name
fi

echo "CHECKING GERRIT FOR OPEN CHANGES"
ssh -p 29418 gerrit-gamma.gic.ericsson.se gerrit query 'status:open project:OSS/com.ericsson.oss.ci.test/eric-oss-gerrit-trigger-test' | grep "number" | cut -d: -f2 | sed 's/^ *//g' > $file_name
sleep 5m

#Remove open changed in Gerrit
echo "LIST FEM's FEEDBACK & REMOVING OPEN CHANGES FROM GERRIT"
for i in `cat open-changes.txt`
do
    ssh -p 29418 gerrit-gamma.gic.ericsson.se gerrit review --abandon $i,1
    echo REMOVED $i
done