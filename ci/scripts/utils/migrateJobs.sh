#!/bin/bash
function moveJobs(){
   local strCurrentJob=$1
   echo "Processing job $strCurrentJob";
   ssh -l ossadmin -p 53801 ${HOST}-eiffel216.eiffel.gic.ericsson.se get-job $strCurrentJob | grep -v 'Skipping' > $strCurrentJob.xml;
   echo "Creating job $strCurrentJob on ${DESTINATION}";
   cat $strCurrentJob.xml | ssh -l ossadmin -p 53801 ${DESTINATION}-eiffel216.eiffel.gic.ericsson.se create-job $strCurrentJob;
   echo "Job(s) moved to ${DESTINATION}";
  # ssh -l edhahim -p 53801 ${HOST}-eiffel216.eiffel.gic.ericsson.se disable-job $strCurrentJob;
  echo "Link to moved job: https://${DESTINATION}-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/$strCurrentJob"
}
# if user COPY_ONLY_EXACT_NAME_JOB = "true" means that only the job with the exact name has to be copied
# else will be copied all jobs that contains the gived input string as subtring in their name
LISTA=($JOB_NAME)
for JOB in ${LISTA[@]};
do
if [ "$COPY_ONLY_EXACT_NAME_JOB" == true ];
then
  for j in $(((ssh -l ossadmin -p 53801 ${HOST}-eiffel216.eiffel.gic.ericsson.se list-jobs All)||(ssh -l ossadmin -p 53801 ${HOST}-eiffel216.eiffel.gic.ericsson.se list-jobs all)) | grep -x ${JOB});
  do
     moveJobs $j
  done
else
  for j in $(((ssh -l ossadmin -p 53801 ${HOST}-eiffel216.eiffel.gic.ericsson.se list-jobs All)||(ssh -l ossadmin -p 53801 ${HOST}-eiffel216.eiffel.gic.ericsson.se list-jobs all) )| grep ${JOB});
  do
     moveJobs $j
  done
fi
done