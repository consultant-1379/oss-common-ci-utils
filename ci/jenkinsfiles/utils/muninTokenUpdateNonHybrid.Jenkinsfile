#!/usr/bin/env groovy
pipeline {
    agent {
        label env.NODE_LABEL
    }
    options {
        timestamps()
        timeout(time: 15, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '15'))
    }
    environment {
        SCRIPT_PATH = "ci/scripts/utils/muninTokenGet.py"
    }
    stages {
        stage('munin_fetch') {
            steps {
                script {
                    sh "python ${env.SCRIPT_PATH}"
                }
            }
        }
    }
    post {
        success {
            mail to: "pdlaeonicc@pdl.internal.ericsson.com",
            from: "jenkins-ossadmin-no-reply@ericsson.com",
            cc: "",
            subject: "Action needed! Update non-hybrid Munin token : ${env.JOB_NAME}",
            body: "Munin Token for non hybrid pipelines needs to be manually updated. <br>" +
            "The value needs be updated for the following credential: <a href='https://fem1s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/credentials/store/system/domain/_/credential/munin-token-manual/'>munin-token-manual</a></p><br>" +
            "Please see <a href='${env.BUILD_URL}'>${env.JOB_NAME}</a> to find the token." +
            "<br><b>Note</b>: This mail has been sent automatically by <a href='${env.BUILD_URL}'>${env.JOB_NAME}</a>",
            mimeType: 'text/html'
        }
    }
}