#!/usr/bin/env groovy

pipeline {

    agent {
        label env.NODE_LABEL
    }

    options {
        timestamps()
        timeout(time: 240, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '15'))
    }

    environment {
        SCRIPT_PATH = "ci/scripts/monitoring/monitoring_GE.py"
        ERROR_REPORT = "Error_logs.txt"
    }

    stages {

        stage('Maven Directory') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        sh "python ${env.SCRIPT_PATH} MavenDirectory"
                    }
                }
            }
        }

        stage('GE Workspace') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        sh "python ${env.SCRIPT_PATH} GEWorkspace"
                    }
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts allowEmptyArchive: true, artifacts: "${env.ERROR_REPORT}"
        }
        unsuccessful {
            sendEmail()
        }
    }
}

def sendEmail() {
    try {
        mail to: "${env.EMAIL}",
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