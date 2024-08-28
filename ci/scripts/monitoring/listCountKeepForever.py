import requests
import os
import sys

JENKINS_URL = os.environ["JENKINS_INSTANCE_URL"]
JENKINS_USER = os.environ.get("GERRIT_USERNAME")
JENKINS_PASSWORD = os.environ.get("GERRIT_PASSWORD")

# Get a list of all jobs
def get_jobs():
    response = requests.get('%s/api/json' % JENKINS_URL, auth=(JENKINS_USER, JENKINS_PASSWORD))
    response.raise_for_status()
    return response.json()['jobs']

# Get a list of all builds for a job
def get_builds(job_name):
    response = requests.get('%s/job/%s/api/json?tree=builds[number,keepLog]' % (JENKINS_URL, job_name), auth=(JENKINS_USER, JENKINS_PASSWORD))
    response.raise_for_status()
    return response.json()['builds']

# Check if a build is marked as "Keep this build forever"
def is_build_kept(build):
    return build['keepLog']

# Main function
def main():
    # Get a list of all jobs
    jobs = get_jobs()
    count = 0

    with open("FEMUsageReport.txt", "a") as report_file:
        print "The jobs that have been chosen to 'keep forever':\n"
        report_file.write("The jobs that have been chosen to 'keep forever':\n")

        # Loop through each job and get a list of all builds
        for job in jobs:
            job_name = job['name']
            builds = get_builds(job_name)

            # Loop through each build and check if it's marked as "Keep this build forever"
            #List and count if any
            for build in builds:
                build_number = build['number']
                if is_build_kept(build):
                    count += 1
                    build_url = "%s/builds/%d" % (job_name, build_number)
                    print build_url
                    report_file.write("%s\n" % build_url)
        print "\nThe number of 'keep forever' builds: %d" % count
        report_file.write("\nThe number of 'keep forever' builds: %d\n" % count)

if __name__ == '__main__':
    main()