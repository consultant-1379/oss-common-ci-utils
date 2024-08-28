#!/usr/bin/env groovy

pipeline {
    agent {
        label env.NODE_LABEL
    }

    options {
        timestamps()
        timeout(time: 60, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '15'))
    }

    stages {
        stage('Prepare') {
            steps {
                script {
                    prepare()
                }
            }
        }

        stage('Add MIMER Access Controls') {
            steps {
                script {
                    update()
                    archiveArtifacts allowEmptyArchive: true, artifacts: "output.txt"
                }
            }
        }
    }
    post {
        unsuccessful {
            email()
        }
    }
}

/* Prepare */
def prepare() {
    // Copy the hybrid project lists from oss-common-ci-utils: dVersion-2.0.0-hybrid to the build/ directory in the Jenkins workspace.
    sh """
        mkdir -p build
        [ -d oss-common-ci-utils ] && rm -rf oss-common-ci-utils
        git clone ${GERRIT_MIRROR}/OSS/com.ericsson.oss.ci/oss-common-ci-utils
        cd oss-common-ci-utils
        git checkout dVersion-2.0.0-hybrid
        cp dsl/projects_list_with_jobs_hybrid ../build
        cp dsl/project_list_with_go_microservices ../build
        cd ..
        [ -d oss-common-ci-utils ] && rm -rf oss-common-ci-utils
    """

    // Output
    sh "touch ${workspace}/output.txt"
}


/* Add MIMER Access Controls */
def update() {
    // Fetch the names of hybrid project lists in the build/ directory and save them to temp.txt
    sh """
        touch ${workspace}/temp.txt
        cd ${workspace}/build/
        ls | tee ${workspace}/temp.txt
    """

    // Fetch the names of Gerrit repositories of MS_LANG projects from the hybrid project lists.
    def gerrit_repo = []
    def gerrit_repo_name = ""
    String[] project_lists = (new File("${workspace}/temp.txt").text).split('\n')
    for (String project_list in project_lists) {
        String[] project_data = (new File("${workspace}/build/${project_list}").text).split('\n')
        for (data in project_data) {
            // The default value of MS_LANG specified in the Jenkins build parameters is "LANG=Java".
            if (data.contains("${env.MS_LANG}")) {
                gerrit_repo_name = data.split(",")[0]
                gerrit_repo.add(gerrit_repo_name)
            }
        }
    }

    // Update each Gerrit repository
    for (repo in gerrit_repo) {
        // Clone Gerrit repository
        print("Clonning ${repo}")
        def artifact_id = ""
        if (repo.contains("adp-ref-app")) {
            artifact_id = repo.split("/")[1]
        } else {
            artifact_id = repo.split("/")[2]
        }

        sh """
            touch ${workspace}/gerrit_push_status.txt
            mkdir ${artifact_id}
            cd ${artifact_id}
            git init
            git pull ${GERRIT_CENTRAL}/"${repo}" refs/meta/config
        """

        if (fileExists("${workspace}/${artifact_id}/groups") && fileExists("${workspace}/${artifact_id}/project.config")) {
            def gerrit_groups_file = new File("${workspace}/${artifact_id}/groups")
            def project_config_file = new File("${workspace}/${artifact_id}/project.config")
            def gerrit_push_status = new File("${workspace}/gerrit_push_status.txt")

            // Gerrit Guard Groups
            // Add Aeonic_CI_admin and GitCA_Replication_DO_NOT_REMOVE to groups
            print("Updating ${repo} groups")
            String gerrit_groups = gerrit_groups_file.text
            if (!gerrit_groups.contains("Aeonic_CI_admin")) {
                gerrit_groups_file.append("c00243cfe9f8ffebc57be4a0dc1e17c4d9a97c7c\tAeonic_CI_admin\n")
                gerrit_push_status.append("true\n")
            }
            if (!gerrit_groups.contains("GitCA_Replication_DO_NOT_REMOVE")) {
                gerrit_groups_file.append("c45bd8129cb909491c2d2cdd84e717ae4b165148\tGitCA_Replication_DO_NOT_REMOVE\n")
                gerrit_push_status.append("true\n")
            }

            // Project Config
            // Add MIMER access controls to project config
            print("Updating ${repo} project.config")
            String project_config = project_config_file.text

            // Mimer-Release-Ready
            if (!project_config.contains("label-Mimer-Release-Ready = -1..+1 group Aeonic_CI_admin")) {
                project_config_file.append('\n[access "refs/*"]\n\tlabel-Mimer-Release-Ready = -1..+1 group Aeonic_CI_admin\n')
                gerrit_push_status.append("true\n")
            }
            if (!project_config.contains('[label "Mimer-Release-Ready"]')) {
                project_config_file.append('[label "Mimer-Release-Ready"]\n\tfunction = NoBlock\n\tvalue = -1 Not release ready\n\tvalue =  0 No Result\n\tvalue = +1 Release ready\n\tdefaultValue = 0\n')
                gerrit_push_status.append("true\n")
            }

            // GitCA_Replication
            if (!project_config.contains('[access "refs/heads/*"]\n\tread = group GitCA_Replication_DO_NOT_REMOVE') && !project_config.contains('[access "refs/heads/*"]\n\040\040\040\040read = group GitCA_Replication_DO_NOT_REMOVE')) {
                project_config_file.append('[access "refs/heads/*"]\n\tread = group GitCA_Replication_DO_NOT_REMOVE\n')
                gerrit_push_status.append("true\n")
            }
            if (!project_config.contains('[access "refs/tags/*"]\n\tread = group GitCA_Replication_DO_NOT_REMOVE') && !project_config.contains('[access "refs/tags/*"]\n\040\040\040\040read = group GitCA_Replication_DO_NOT_REMOVE')) {
                project_config_file.append('[access "refs/tags/*"]\n\tread = group GitCA_Replication_DO_NOT_REMOVE\n')
                gerrit_push_status.append("true\n")
            }

            // Push changes
            def output = new File("${workspace}/output.txt")
            if (gerrit_push_status.text.contains("true")) {
                sh """
                    cd ${artifact_id}
                    git add .
                    git commit -m "Added MIMER Access controls"
                    git push ssh://gerrit-gamma.gic.ericsson.se:29418/"${repo}" HEAD:refs/meta/config
                    cd ..
                """
                output.append("${repo} : Added MIMER Access controls.\n")
            } else {
                output.append("${repo} : Access controls necessary for MIMER are in place.\n")
            }
        }

        // Cleanup
        sh """
            rm -rf ${workspace}/${artifact_id}
            rm -f ${workspace}/gerrit_push_status.txt
        """
    }
    // Cleanup
    sh "rm -f ${workspace}/temp.txt"
    sh "rm -rf ${workspace}/build"
}


/* Failure Notification */
def email() {
    try {
        mail to: "${env.DISTRIBUTION_LIST}",
        from: "jenkins-ossadmin-no-reply@ericsson.com",
        cc: "",
        subject: "Action Required! Failure in ${env.JOB_NAME}",
        body: "The build <a href='${env.BUILD_URL}'>#${env.BUILD_NUMBER}</a> of ${env.JOB_NAME} has failed!<br>" +
              "Please have a look into this and take appropriate action!<br>" +
              "<br><b>Note</b>: This mail has been sent automatically by <a href='${env.BUILD_URL}'>${env.JOB_NAME}</a>",
        mimeType: "text/html"
    } catch (Exception e) {
        echo "Email notification was not sent!"
        print e
    }
}