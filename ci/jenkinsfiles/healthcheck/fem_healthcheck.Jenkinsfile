#!/usr/bin/env groovy

def bob = 'python3 bob/bob.py'
def eriDocInstance = "https://eridoc.internal.ericsson.com/eridoc/"
pipeline {
    agent {
        node {
            label NODE_LABEL
        }
    }

    options {
        timestamps()
        timeout(time: 5, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '15'))
    }

    environment {
        SCRIPT = 'ci/scripts/healthchecks/fem_healthcheck.py'
    }

    stages {
        stage('FEM') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        withCredentials([usernamePassword(credentialsId: 'GERRIT_PASSWORD', usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                            sh "python ${env.SCRIPT} FEM"
                        }
                    }
                }
            }
        }

        stage('Email') {
            steps {
                sh "python ${env.SCRIPT} Email"
            }
        }
    }
    post {
        always {
            archiveArtifacts allowEmptyArchive: true, artifacts: "healthcheck_file.txt"
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