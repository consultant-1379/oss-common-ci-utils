#!/usr/bin / env groovy

def ruleset = "ci/rulesets/healthcheck/xray_healthcheck_ruleset.yaml"
def bob = "python3 bob/bob.py -r ${ruleset}"

pipeline {
    agent {
        label env.NODE_LABEL
    }

    options {
        timestamps()
        timeout(time: 15, unit: "MINUTES")
        buildDiscarder(logRotator(numToKeepStr: "15", artifactNumToKeepStr: "15"))
    }

    stages {
        stage("Prepare") {
            steps {
                sh "git submodule add ../../../adp-cicd/bob"
            }
        }

        stage("Xray") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'SELI_ARTIFACTORY', usernameVariable: 'SELI_ARTIFACTORY_REPO_USER', passwordVariable: 'SELI_ARTIFACTORY_REPO_PASS')]) {
                        sh "${bob} xray-scan"
                    }
                }
            }
        }
    }
    post {
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
            subject: "Xray failure! Action required! Failure in ${env.JOB_NAME}",
            body: "The build <a href='${env.BUILD_URL}'>#${env.BUILD_NUMBER}</a> of ${env.JOB_NAME} has failed!<br>" +
            "Please have a look into this and take appropriate action!<br>" +
            "<br><b>Note</b>: This mail has been sent automatically by <a href='${env.BUILD_URL}'>${env.JOB_NAME}</a>",
            mimeType: "text/html"
    } catch (Exception e) {
        echo "Email notification was not sent!"
        print e
    }
}