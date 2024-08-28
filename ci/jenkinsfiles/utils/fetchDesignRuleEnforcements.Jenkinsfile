#!/usr/bin / env groovy

pipeline {
    agent {
        label env.NODE_LABEL
    }

    options {
        timestamps()
        timeout(time: 10, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '15'))
    }

    environment {
        REPORT_DIRECTORY = 'DR_Enforcements'
        REPORT = "${WORKSPACE}/${env.REPORT_DIRECTORY}/ADP_DR_Enforcement_Data.csv"
        REPORT_UPLOAD_URL = "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/monitoring/DR_Enforcements/ADP_DR_Enforcement_Data.csv"
        SCRIPT = 'ci/scripts/utils/fetchDesignRuleEnforcements.py'
    }

    stages {
        stage('Prepare') {
            steps {
                script {
                    sh "rm -rf ${env.REPORT_DIRECTORY} && mkdir -p ${env.REPORT_DIRECTORY}"
                }
            }
        }

        stage('Fetch DR Enforcements') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'GERRIT_PASSWORD', usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                        sh "python ${env.SCRIPT} fetchDesignRuleEnforcements"
                    }
                }
            }
        }

        stage('Upload') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'SELI_ARTIFACTORY', usernameVariable: 'SELI_ARTIFACTORY_REPO_USER', passwordVariable: 'SELI_ARTIFACTORY_REPO_PASS')]) {
                        sh "curl -u ${SELI_ARTIFACTORY_REPO_USER}:${SELI_ARTIFACTORY_REPO_PASS} -X PUT -T ${env.REPORT} ${env.REPORT_UPLOAD_URL}"
                    }
                }
            }
        }

    }
    post {
        success {
            archiveArtifacts allowEmptyArchive: true, artifacts: "${env.REPORT_DIRECTORY}/*"
        }
        unsuccessful {
            sendEmail()
        }
    }
}

def sendEmail() {
    try {
        mail to: "${env.DISTRIBUTION_LIST}",
            from: "jenkins-ossadmin-no-reply@ericsson.com",
            cc: "",
            subject: "Action Required! Failure in ${env.JOB_NAME}",
            body: "The build <a href='${env.BUILD_URL}'>#${env.BUILD_NUMBER}</a> of ${env.JOB_NAME} has failed!<br>" +
            "Please have a look into this and take appropriate action!<br>" +
            "<br><b>Note</b>: This mail has been sent automatically by <a href='${env.BUILD_URL}'>${env.JOB_NAME}</a>",
            mimeType: 'text/html'
    } catch (Exception e) {
        echo "Email notification was not sent!"
        print e
    }
}