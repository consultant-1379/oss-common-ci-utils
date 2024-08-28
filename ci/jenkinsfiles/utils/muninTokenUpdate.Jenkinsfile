#!/usr/bin/env groovy
pipeline {
    agent { label env.NODE_LABEL }
    options {
        timestamps()
        timeout(time: 15, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '15'))
    }
    environment {
        SCRIPT_PATH = "ci/scripts/utils/muninTokenUpdate.py"
    }
    stages {
        stage('Retrieve Munin Tokens') {
            steps {
                script {
                    sh "python ${env.SCRIPT_PATH}"
                }
            }
        }
    }
    post {
        failure {
            mail to: "pdlaeonicc@pdl.internal.ericsson.com",
            from: "jenkins-ossadmin-no-reply@ericsson.com",
            cc: "",
            subject: "Action Required! Failure to retrieve Munin Token! ${env.JOB_NAME}",
            body: "The build <a href='${env.BUILD_URL}'>#${env.BUILD_NUMBER}</a> of ${env.JOB_NAME} has failed!<br>" +
            "Please investigate and take appropriate action!<br>" +
            "<br><b>Note</b>: This mail has been sent automatically by <a href='${env.BUILD_URL}'>${env.JOB_NAME}</a>",
            mimeType: 'text/html'
        }
    }
}